"""
Testes da lógica de scoring. Tudo OFFLINE: o LLM é mockado.

Cobre:
- score_heuristico (determinístico, sem rede)
- parse_cv num CV de exemplo de verdade (LLM de extração mockado)
- match_score: confere o blend 0.4 * heurística + 0.6 * LLM
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from src import scoring

CV_EXEMPLO = (
    Path(__file__).resolve().parent.parent
    / "data" / "cvs-exemplos" / "cv-001-joao-silva.txt"
)

VAGA = {
    "titulo": "AI Engineer Pleno",
    "descricao": "vaga de exemplo",
    "skills_obrigatorias": ["Python", "FastAPI", "Docker", "LLM", "PostgreSQL"],
}


def test_score_heuristico_overlap_parcial():
    # 3 de 5 skills batem (case-insensitive) -> 60
    cv = {"skills": ["python", "FastAPI", "postgresql", "git"]}
    assert scoring.score_heuristico(cv, VAGA) == 60


def test_score_heuristico_sem_skills_na_vaga_nao_quebra():
    # divisão por zero protegida: total mínimo = 1
    cv = {"skills": ["python"]}
    vaga = {"skills_obrigatorias": []}
    assert scoring.score_heuristico(cv, vaga) == 0


def test_parse_cv_le_arquivo_real_e_estrutura(monkeypatch):
    assert CV_EXEMPLO.exists(), "CV de exemplo sumiu do data/"

    capturado = {}

    def fake_chamar_llm(prompt: str) -> dict:
        # confirma que o texto do CV real chegou no prompt de extração
        capturado["prompt"] = prompt
        return {
            "nome": "João Henrique da Silva Neto",
            "email": "joao.silva.exemplo@email-ficticio.com.br",
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
            "anos_experiencia_total": 5,
            "formacao": [],
            "experiencia": [],
        }

    monkeypatch.setattr(scoring, "_chamar_llm", fake_chamar_llm)

    cv = scoring.parse_cv(str(CV_EXEMPLO))

    # asserts em ASCII de propósito (console Windows mangla acento) — prova
    # que o arquivo real foi lido e o texto chegou no prompt de extração.
    assert "FastAPI" in capturado["prompt"]
    assert "joao.silva.exemplo@email-ficticio.com.br" in capturado["prompt"]
    assert "FastAPI" in cv["skills"]


def test_match_score_aplica_blend_0_4_0_6(monkeypatch):
    # heurística: 4 de 5 -> 80 ; LLM (mock) -> 60
    # final = int(0.4*80 + 0.6*60) = int(32 + 36) = 68
    cv = {"skills": ["python", "fastapi", "docker", "postgresql"]}

    monkeypatch.setattr(
        scoring,
        "avaliar_com_llm",
        lambda c, v: {"score_llm": 60, "justificativa": "ok (mock)"},
    )

    out = scoring.match_score(cv, VAGA)
    assert out["score_heuristico"] == 80
    assert out["score_llm"] == 60
    assert out["score_final"] == 68
    assert out["modelo"] == scoring.MODEL
    assert out["justificativa"] == "ok (mock)"


@pytest.mark.parametrize(
    "resposta",
    [
        '{"score_llm": 82, "justificativa": "Boa aderência"}',
        'Resultado da análise:\n```json\n{"score_llm": 82, "justificativa": "Boa aderência"}\n```',
    ],
)
def test_chamar_llm_usa_anthropic_e_retorna_json(monkeypatch, resposta):
    chamada = {}

    class FakeAnthropic:
        def __init__(self, api_key):
            chamada["api_key"] = api_key
            self.messages = self

        def create(self, **kwargs):
            chamada["request"] = kwargs
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        type="text",
                        text=resposta,
                    )
                ]
            )

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(scoring, "Anthropic", FakeAnthropic)

    resultado = scoring._chamar_llm("prompt de teste")

    assert chamada["api_key"] == "test-key"
    assert chamada["request"]["model"] == "claude-haiku-4-5-20251001"
    assert chamada["request"]["max_tokens"] == 4096
    assert chamada["request"]["temperature"] == 0
    assert chamada["request"]["messages"] == [
        {"role": "user", "content": "prompt de teste"}
    ]
    assert resultado == {"score_llm": 82, "justificativa": "Boa aderência"}


def test_chamar_llm_falha_com_resposta_sem_json_valido(monkeypatch):
    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = self

        def create(self, **kwargs):
            return SimpleNamespace(
                content=[SimpleNamespace(type="text", text="Não foi possível analisar.")]
            )

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(scoring, "Anthropic", FakeAnthropic)

    with pytest.raises(ValueError, match="não retornou um objeto JSON"):
        scoring._chamar_llm("prompt de teste")


def test_chamar_llm_falha_sem_chave_anthropic(monkeypatch):
    class FakeAnthropic:
        def __init__(self, api_key):
            raise AssertionError("O client não deve ser criado sem chave.")

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(scoring, "Anthropic", FakeAnthropic)

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        scoring._chamar_llm("prompt de teste")
