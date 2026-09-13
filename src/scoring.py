"""
Lógica de scoring do TalentoBR CV Screener.

Esse arquivo é, basicamente, o miolo do notebook v0.4 do time de Data
extraído pra um módulo de verdade. A matemática do score continua a mesma:

    score_final = 0.4 * score_heuristico + 0.6 * score_llm

A heurística é determinística (overlap de skills). A parte do LLM é o
"julgamento" + justificativa em texto livre.

OBS importantes (leia antes de confiar nisso):
- A "justificativa" é gerada pelo próprio modelo DEPOIS do score. É post-hoc,
  não é explicação fiel. Não use como laudo.
- O viés que a gente observou no notebook (mulher e 50+ pontuando menos,
  universidade de capital pontuando mais, currículo em inglês pontuando mais)
  CONTINUA AQUI. Não foi mitigado. Ver README -> "Dívida técnica herdada".
- Provedor: OpenAI, um GPT pequeno (trocamos de um GPT grande pra cortar ~10x de custo).
  Alternativa que cabe sem reescrever muito: Anthropic, um modelo Claude pequeno
  (precisa instalar o SDK `anthropic` e adaptar `_chamar_llm`).

TODO (quem pegar): versionar o prompt, medir custo real, e por favor escrever
o mapa de viés antes de qualquer deploy.
"""

import os
import json
from pathlib import Path

# Modelo barato. Era um GPT grande no notebook, mas pra 10k CVs/mês não fecha o budget.
MODEL = "gpt-5.4-mini"

# Pesos do blend. Hardcoded mesmo — TODO: virar config/env e justificar a escolha.
PESO_HEURISTICA = 0.4
PESO_LLM = 0.6


# ---------------------------------------------------------------------------
# Cliente LLM (criado de forma preguiçosa pra não quebrar import sem chave)
# ---------------------------------------------------------------------------

def _get_client():
    """Cria o client da OpenAI sob demanda.

    Lê a chave crua do ambiente. Sem fallback, sem cofre de segredos, sem nada.
    Se não tiver OPENAI_API_KEY setada, estoura aqui mesmo (de propósito).
    """
    from openai import OpenAI  # import tardio: testes offline não precisam do SDK

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não configurada. Crie um .env (veja .env.example)."
        )
    return OpenAI(api_key=api_key)


def _chamar_llm(prompt: str) -> dict:
    """Faz uma chamada de chat pedindo JSON e devolve o dict já parseado.

    Centralizado aqui de propósito: nos testes a gente faz monkeypatch DESTA
    função, então nenhuma chamada de rede acontece offline.
    """
    client = _get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)


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
