"""
Teste do endpoint POST /score com FastAPI TestClient.

OFFLINE: as duas chamadas de LLM (extração de campos e julgamento) são
mockadas via monkeypatch no módulo `src.scoring`. Nenhuma rede é tocada.
"""

import pytest
from fastapi.testclient import TestClient

import app as app_module
from src import scoring


@pytest.fixture
def client(monkeypatch):
    # extração de campos -> dict fixo
    monkeypatch.setattr(
        scoring,
        "extrair_campos",
        lambda texto: {
            "nome": "Candidato Teste",
            "email": "teste@exemplo.com",
            "skills": ["Python", "FastAPI", "Docker"],
            "anos_experiencia_total": 4,
            "formacao": [],
            "experiencia": [],
        },
    )
    # julgamento LLM -> score fixo
    monkeypatch.setattr(
        scoring,
        "avaliar_com_llm",
        lambda cv, vaga: {"score_llm": 70, "justificativa": "match razoável (mock)"},
    )
    # app.py importou `extrair_campos` por referência; reaponta lá também
    monkeypatch.setattr(app_module, "extrair_campos", scoring.extrair_campos)
    return TestClient(app_module.app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_score_endpoint(client):
    payload = {
        "cv_texto": "qualquer texto de cv aqui",
        "vaga": {
            "titulo": "AI Engineer Pleno",
            "descricao": "x",
            "skills_obrigatorias": ["Python", "FastAPI", "Docker", "LLM", "PostgreSQL"],
        },
    }
    r = client.post("/score", json=payload)
    assert r.status_code == 200
    data = r.json()

    # heurística: 3 de 5 -> 60 ; LLM mock -> 70
    # final = int(0.4*60 + 0.6*70) = int(24 + 42) = 66
    assert data["score_heuristico"] == 60
    assert data["score_llm"] == 70
    assert data["score_final"] == 66
    assert data["candidato"]["nome"] == "Candidato Teste"
    assert "Art. 20" in data["aviso"]


def test_score_endpoint_valida_payload(client):
    # falta `vaga` -> 422 do pydantic/FastAPI
    r = client.post("/score", json={"cv_texto": "só o cv"})
    assert r.status_code == 422
