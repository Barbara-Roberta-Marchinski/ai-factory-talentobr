from dotenv import load_dotenv
load_dotenv()

import os
import json
import hashlib
import logging
import re
import time
from copy import deepcopy
from pathlib import Path
from anthropic import Anthropic
from langfuse import observe, propagate_attributes
import requests

logger = logging.getLogger(__name__)


def disparar_alerta_erro(mensagem: str):
    webhook_url = os.getenv("WEBHOOK_ALERTA")
    if not webhook_url:
        logger.warning(
            "WEBHOOK_ALERTA não configurada; alerta não enviado."
        )
        return

    try:
        # Payload Adaptive Card envelopado para o novo Teams Workflows
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": "🚨 ALERTA - Falha na aplicação",
                                "weight": "Bolder",
                                "size": "Medium",
                                "color": "Attention"
                            },
                            {
                                "type": "TextBlock",
                                "text": mensagem,
                                "wrap": True
                            }
                        ]
                    }
                }
            ]
        }
        response = requests.post(webhook_url, json=payload, timeout=5)
        if not 200 <= response.status_code < 300:
            logger.error(
                "Webhook de alerta respondeu com HTTP %s; alerta não confirmado.",
                response.status_code,
            )
            return
        logger.info("Alerta aceito pelo webhook (HTTP %s).", response.status_code)
    except requests.RequestException as error:
        # A exceção pode conter a URL secreta do workflow; não registrar sua mensagem.
        logger.error(
            "Falha ao enviar alerta webhook (%s).",
            type(error).__name__,
        )


def sanitizar_pii(texto: str) -> str:
    """Substitui dados de contato e identificadores comuns antes do uso externo."""
    texto = re.sub(
        r"(?i)\b(?:https?://)?(?:www\.)?(?:linkedin\.com|github\.com)/[^\s<>()]+",
        "[LINK_REMOVIDO]",
        texto,
    )
    texto = re.sub(
        r"(?i)\b[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?"
        r"(?:\.[A-Z0-9](?:[A-Z0-9-]*[A-Z0-9])?)+\b",
        "[EMAIL_REMOVIDO]",
        texto,
    )
    texto = re.sub(
        r"(?<!\d)(?:\d{3}\.?\d{3}\.?\d{3}-?\d{2})(?!\d)",
        "[CPF_REMOVIDO]",
        texto,
    )
    texto = re.sub(
        r"(?<!\d)(?:\+?55[\s.-]*)?(?:\(?\d{2}\)?[\s.-]*)?"
        r"(?:9\d{4}|\d{4})[\s.-]?\d{4}(?!\d)",
        "[TELEFONE_REMOVIDO]",
        texto,
    )
    return texto



# Modelo usado para chamadas de extração e scoring.
MODEL = "claude-haiku-4-5-20251001"

# Pesos do blend. Hardcoded mesmo — TODO: virar config/env e justificar a escolha.
PESO_HEURISTICA = 0.4
PESO_LLM = 0.6

CACHE_AVALIACOES = {}


# ---------------------------------------------------------------------------
# Cliente LLM (criado de forma preguiçosa pra não quebrar import sem chave)
# ---------------------------------------------------------------------------

def _get_client():
    """Cria o client da Anthropic sob demanda.

    Lê a chave do ambiente. Se ANTHROPIC_API_KEY não estiver configurada,
    falha explicitamente.
    """
    

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY não configurada. Configure a chave no ambiente."
        )
    return Anthropic(api_key=api_key)


def _parse_json_object(text: str) -> dict:
    """Parseia o primeiro objeto JSON, mesmo com texto explicativo ao redor."""
    start = text.find("{")
    if start == -1:
        raise ValueError("A API da Anthropic não retornou um objeto JSON.")

    try:
        result, _ = json.JSONDecoder().raw_decode(text, start)
    except json.JSONDecodeError as error:
        raise ValueError(
            "A API da Anthropic retornou uma resposta que não contém JSON válido."
        ) from error

    if not isinstance(result, dict):
        raise ValueError("A API da Anthropic não retornou um objeto JSON.")
    return result


def _chamar_llm(prompt: str) -> dict:
    """Faz uma chamada de chat pedindo JSON e devolve o dict já parseado."""
    client = _get_client()
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    texto = "".join(bloco.text for bloco in resp.content if bloco.type == "text")
    if not texto:
        raise ValueError("A API da Anthropic retornou uma resposta sem texto.")
    return _parse_json_object(texto)


# ---------------------------------------------------------------------------
# Parsing de CV
# ---------------------------------------------------------------------------

def ler_texto_cv(path: str) -> str:
    """Lê o texto bruto de um CV (.pdf ou .txt)."""
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        import pypdf  # import tardio: só precisa do pypdf pra PDF

        reader = pypdf.PdfReader(str(p))
        # extract_text() volta None às vezes em página sem texto (PDF escaneado).
        # Não tratamos OCR. CV escaneado vira lixo silenciosamente. TODO.
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return p.read_text(encoding="utf-8")


def extrair_campos(texto: str) -> dict:
    """Usa o LLM pra transformar o texto bruto do CV em campos canônicos.

    Retorna um dict com: nome, email, formacao[], experiencia[], skills[],
    anos_experiencia_total. É esta função (via `_chamar_llm`) que os testes
    mockam.
    """
    texto_sanitizado = sanitizar_pii(texto)
    prompt = f"""Extraia do curriculo abaixo um JSON com os campos:
- nome (string)
- email (string)
- formacao (lista de objetos: instituicao, curso, ano_conclusao)
- experiencia (lista de objetos: empresa, cargo, periodo, descricao)
- skills (lista de strings)
- anos_experiencia_total (int)

Responda APENAS com o JSON, sem markdown.

CURRICULO:
{texto_sanitizado}
"""
    return _chamar_llm(prompt)


def parse_cv(path: str) -> dict:
    """Lê um CV de disco (PDF/TXT) e devolve os campos estruturados via LLM."""
    texto = ler_texto_cv(path)
    return extrair_campos(texto)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_heuristico(cv_dict: dict, vaga_dict: dict) -> int:
    """Heurística determinística: % de skills obrigatórias que o CV cobre.

    Bem ingênua de propósito: é só interseção de conjuntos, case-insensitive,
    sem stemming, sem sinônimos ("Postgres" != "PostgreSQL"), e IGNORA
    `anos_experiencia_total` (que a gente nem usa, apesar do README antigo
    dizer que usava). Quem pegar: melhore isso, é dívida.
    """
    cv_skills = {s.lower().strip() for s in cv_dict.get("skills", [])}
    vaga_skills = {s.lower().strip() for s in vaga_dict.get("skills_obrigatorias", [])}
    overlap = len(cv_skills & vaga_skills)
    total = max(len(vaga_skills), 1)
    return int(100 * overlap / total)


@observe(capture_input=False, capture_output=False)
def avaliar_com_llm(cv_dict: dict, vaga_dict: dict) -> dict:
    """Pede ao LLM um score 0-100 + justificativa curta em pt-BR.

    Retorna {"score_llm": int, "justificativa": str}. Mockada nos testes.
    """
    inicio_trace = time.time()
    cv_texto = json.dumps(cv_dict, ensure_ascii=False, sort_keys=True)
    vaga_texto = json.dumps(vaga_dict, ensure_ascii=False, sort_keys=True)
    cv_hash = hashlib.sha256(cv_texto.encode("utf-8")).hexdigest()[:8]

    vaga_hash = hashlib.sha256(vaga_texto.encode("utf-8")).hexdigest()[:8]
    chave_cache = f"{cv_hash}_{vaga_hash}"
    logger.info(
        "[VOLUME] Iniciando Trace para avaliação do CV. Referência: %s",
        chave_cache,
    )
    with propagate_attributes(session_id=cv_hash, tags=["cv_screening"]):
        return _avaliar_com_llm_com_cache(
            cv_dict=cv_dict,
            cv_texto=cv_texto,
            vaga_dict=vaga_dict,
            chave_cache=chave_cache,
            inicio_trace=inicio_trace,
        )

def _avaliar_com_llm_com_cache(
    cv_dict: dict,
    cv_texto: str,
    vaga_dict: dict,
    chave_cache: str,
    inicio_trace: float,
) -> dict:
    if chave_cache in CACHE_AVALIACOES:
        latencia = time.time() - inicio_trace
        logger.info(
            "[LATÊNCIA] Span Cache: %.4fs (Cache Hit rápido)",
            latencia,
        )
        logger.info("[CUSTO] $0.00 e 0 tokens gastos (Economia via Cache)")
        logger.info(
            "[QUALIDADE] Score recuperado com sucesso e consistência do cache."
        )
        return deepcopy(CACHE_AVALIACOES[chave_cache])

    candidato_sanitizado = sanitizar_pii(cv_texto)
    prompt = f"""Voce e um recrutador experiente. Avalie o match entre o candidato e a vaga.
Responda JSON com os campos: score_llm (0-100), justificativa (string curta em pt-BR).

VAGA:
{json.dumps(vaga_dict, ensure_ascii=False, indent=2)}

CANDIDATO:
{candidato_sanitizado}
"""
    try:
        out = _chamar_llm(prompt)
    except Exception as error:
        logger.error(
            "[ERRO] Falha na avaliação Ref: %s tipo_erro=%s",
            chave_cache,
            type(error).__name__,
        )
        raise

    resposta = {
        "score_llm": int(out.get("score_llm", 0)),
        "justificativa": out.get("justificativa", ""),
    }
    latencia = time.time() - inicio_trace
    logger.info("[LATÊNCIA] Span LLM: %.4fs (Cache Miss)", latencia)
    logger.info(
        "[CUSTO] Chamada ao provedor realizada; tokens e custo não disponíveis "
        "neste fluxo."
    )
    logger.info("[QUALIDADE] Avaliação gerada pela IA com sucesso.")
    CACHE_AVALIACOES[chave_cache] = deepcopy(resposta)
    return resposta


def match_score(cv_dict: dict, vaga_dict: dict) -> dict:
    """Combina heurística (0.4) + LLM (0.6) num score final 0-100.

    É APOIO à decisão do recrutador, NÃO decisão automática (LGPD Art. 20).
    A UI deve deixar isso explícito e permitir o recrutador discordar.
    """
    sh = score_heuristico(cv_dict, vaga_dict)
    aval = avaliar_com_llm(cv_dict, vaga_dict)
    score_llm = aval["score_llm"]
    score_final = int(PESO_HEURISTICA * sh + PESO_LLM * score_llm)
    return {
        "score_final": score_final,
        "score_heuristico": sh,
        "score_llm": score_llm,
        "justificativa": aval["justificativa"],
        "modelo": MODEL,
        # SEM log de auditoria aqui. LGPD Art. 20 exige rastro. Dívida herdada.
    }
