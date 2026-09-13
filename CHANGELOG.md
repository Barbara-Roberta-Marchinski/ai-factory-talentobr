# Changelog

## [v0.5] (Data Team — handoff)
- Notebook virou protótipo rodável: pacote `src/` + API + UI.
- `src/scoring.py`: lógica do notebook extraída (parse_cv, score_heuristico,
  avaliar_com_llm, match_score) com client LLM lazy e ponto único de chamada
  (`_chamar_llm`) pra facilitar mock nos testes.
- `app.py`: API FastAPI com `POST /score` e `GET /health`.
- `ui.py`: UI Streamlit do recrutador (consome a API), com botões de decisão
  humana (apoio, não automação — LGPD Art. 20). Botões ainda NÃO persistem.
- Troca de modelo: um GPT grande -> um GPT pequeno (corte de custo ~10x).
- `tests/`: suíte pytest OFFLINE (LLM mockado). 7 testes passando.
- requirements.txt repinado (fastapi, uvicorn, streamlit, openai, pypdf, etc.);
  removido pandas (não usado). `.env.example` e `.gitignore` ajustados.
- Dívida técnica plantada e documentada no README ("Dívida técnica herdada").

## [v0.4] (Data Team)
- Parsing PDF funcional
- Scoring híbrido LLM + heurística
- 5 CVs de teste

## [v0.3]
- Primeira versão LLM-only (sem heurística)
