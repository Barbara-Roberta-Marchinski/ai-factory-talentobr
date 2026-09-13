"""
API de scoring do TalentoBR CV Screener.

Roda com:  uvicorn app:app --reload
Sobe em:   http://localhost:8000  (docs em /docs)

Endpoint principal: POST /score
Recebe o texto de um CV + a vaga, devolve score 0-100 + justificativa.

ATENÇÃO (dívida herdada, ver README):
- NÃO tem autenticação. NÃO é multi-tenant. Qualquer um que alcançar a porta
  manda CV pra dentro. Cliente A e cliente B compartilhariam tudo. NÃO suba isso
  exposto.
- NÃO tem log de auditoria (LGPD Art. 20). Nada é persistido.
- Sem rate limit, sem cache, sem observabilidade.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.scoring import extrair_campos, match_score

app = FastAPI(
    title="TalentoBR CV Screener API",
    version="0.5",
    description="Protótipo de triagem de CVs. APOIO à decisão humana, não decisão automática (LGPD Art. 20).",
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class Vaga(BaseModel):
    titulo: str
    descricao: str = ""
    skills_obrigatorias: list[str] = Field(default_factory=list)


class ScoreRequest(BaseModel):
    cv_texto: str = Field(..., description="Texto bruto do currículo (já extraído do PDF/TXT).")
    vaga: Vaga


class ScoreResponse(BaseModel):
    score_final: int
    score_heuristico: int
    score_llm: int
    justificativa: str
    modelo: str
    candidato: dict
    # Lembrete pro front: SEMPRE mostrar que é apoio e permitir revisão humana.
    aviso: str = "Resultado de apoio à triagem. A decisão é do recrutador (LGPD Art. 20)."


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "versao": app.version}


@app.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest):
    """Pontua um CV contra uma vaga.

    Fluxo: texto bruto -> extração de campos (LLM) -> match_score (heurística + LLM).
    """
    cv_dict = extrair_campos(req.cv_texto)
    vaga_dict = req.vaga.model_dump()
    resultado = match_score(cv_dict, vaga_dict)
    resultado["candidato"] = cv_dict
    return resultado
