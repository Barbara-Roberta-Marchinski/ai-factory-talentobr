import logging
import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse
import logging
logging.basicConfig(level=logging.INFO)


from src.scoring import disparar_alerta_erro, extrair_campos, match_score



logger = logging.getLogger(__name__)

app = FastAPI(
    title="TalentoBR CV Screener API",
    version="0.5",
    description="Protótipo de triagem de CVs. APOIO à decisão humana, não decisão automática (LGPD Art. 20).",
)


def _contexto_erro(request: Request, status_code: int, tipo: str) -> str:
    route = request.scope.get("route")
    endpoint = getattr(route, "path", request.url.path)
    return (
        f"HTTP {status_code} em {request.method} {endpoint}. "
        f"Tipo: {tipo}."
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request, error: RequestValidationError
):
    await run_in_threadpool(
        disparar_alerta_erro,
        _contexto_erro(request, 422, "RequestValidationError"),
    )
    return await request_validation_exception_handler(request, error)


@app.exception_handler(StarletteHTTPException)
async def tratar_erro_http(request: Request, error: StarletteHTTPException):
    if error.status_code >= 400:
        await run_in_threadpool(
            disparar_alerta_erro,
            _contexto_erro(
                request,
                error.status_code,
                "HTTPException",
            )
        )
    return await http_exception_handler(request, error)


@app.exception_handler(Exception)
async def tratar_erro_interno(request: Request, error: Exception):
    tipo_erro = type(error).__name__
    logger.exception(
        "Falha não tratada (%s) em %s %s",
        tipo_erro,
        request.method,
        getattr(request.scope.get("route"), "path", request.url.path),
    )
    await run_in_threadpool(
        disparar_alerta_erro,
        _contexto_erro(request, 500, tipo_erro),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
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
    cv_dict.pop("nome", None)
    vaga_dict = req.vaga.model_dump()
    resultado = match_score(cv_dict, vaga_dict, cv_texto=req.cv_texto)
    resultado["candidato"] = cv_dict
    return resultado
