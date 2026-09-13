"""
Testes da lógica de scoring. Tudo OFFLINE: o LLM é mockado.

Cobre:
- score_heuristico (determinístico, sem rede)
- parse_cv num CV de exemplo de verdade (LLM de extração mockado)
- match_score: confere o blend 0.4 * heurística + 0.6 * LLM
"""

from pathlib import Path

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
