# Changelog

## [v0.6] (Outubro de 2026 — migração para frontend web)
- Migração da interface Streamlit para Next.js + React + Tailwind em
  `talentobr-web/`, configurado com export estático para hospedagem como
  Static Site no Render.
- Formulário de vaga e currículo, upload de arquivos TXT/PDF com extração de
  texto no navegador, estados de carregamento/erro/sucesso e painel de scores,
  justificativa LLM e revisão humana.
- Integração do frontend via `NEXT_PUBLIC_API_BASE_URL`; exemplos e instruções
  locais e de deploy atualizados nos READMEs.
- CORS do FastAPI configurável por `FRONTEND_ORIGINS`, limitado às origens
  informadas, com testes de preflight permitido e origem rejeitada.
- Remoção de `ui.py` e das dependências Streamlit/Requests do backend.
- Atualização do modelo Anthropic para `claude-haiku-4-5-20251001`.
- Parsing da resposta LLM agora aceita objeto JSON acompanhado de texto ou
  bloco Markdown e falha explicitamente se não houver um objeto válido.
- Testes ampliados para modelo, parsing JSON e CORS; suíte validada com
  13 testes aprovados.

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
