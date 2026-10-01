

import os
import json
from pathlib import Path
from anthropic import Anthropic

# Modelo pequeno para chamadas de extração e scoring.
MODEL = "claude-3-5-sonnet-20241022"

# Pesos do blend. Hardcoded mesmo — TODO: virar config/env e justificar a escolha.
PESO_HEURISTICA = 0.4
PESO_LLM = 0.6


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


def _chamar_llm(prompt: str) -> dict:
    """Faz uma chamada de chat pedindo JSON e devolve o dict já parseado.

    Centralizado aqui de propósito: nos testes a gente faz monkeypatch DESTA
    função, então nenhuma chamada de rede acontece offline.
    """
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
    return json.loads(texto)


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
    prompt = f"""Extraia do curriculo abaixo um JSON com os campos:
- nome (string)
- email (string)
- formacao (lista de objetos: instituicao, curso, ano_conclusao)
- experiencia (lista de objetos: empresa, cargo, periodo, descricao)
- skills (lista de strings)
- anos_experiencia_total (int)

Responda APENAS com o JSON, sem markdown.

CURRICULO:
{texto}
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


def avaliar_com_llm(cv_dict: dict, vaga_dict: dict) -> dict:
    """Pede ao LLM um score 0-100 + justificativa curta em pt-BR.

    Retorna {"score_llm": int, "justificativa": str}. Mockada nos testes.
    """
    prompt = f"""Voce e um recrutador experiente. Avalie o match entre o candidato e a vaga.
Responda JSON com os campos: score_llm (0-100), justificativa (string curta em pt-BR).

VAGA:
{json.dumps(vaga_dict, ensure_ascii=False, indent=2)}

CANDIDATO:
{json.dumps(cv_dict, ensure_ascii=False, indent=2)}
"""
    out = _chamar_llm(prompt)
    return {
        "score_llm": int(out.get("score_llm", 0)),
        "justificativa": out.get("justificativa", ""),
    }


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
