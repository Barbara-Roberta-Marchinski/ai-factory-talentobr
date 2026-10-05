import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.scoring import extrair_campos, match_score

app = FastAPI(
    title="TalentoBR CV Screener API",
    version="0.5",
    description="Protótipo de triagem de CVs. APOIO à decisão humana, não decisão automática (LGPD Art. 20).",
)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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
