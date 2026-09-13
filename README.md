# TalentoBR — CV Screener (passagem de bastão do time de Data)

Oi. Aqui é o time de Data da TalentoBR. 👋

Esse repo era um notebook (`notebook-skeleton.ipynb`) que pontuava currículo
contra vaga. A gente "promoveu" ele pra um protótipo que **roda de verdade**:
uma API (FastAPI) + uma telinha de recrutador (Streamlit), reaproveitando a
MESMA lógica de scoring do notebook (parsing + heurística + LLM).

Importante deixar claro de cara: **isto é um ponto de partida, não uma solução.**
Está uns 40% pronto. Tem dívida técnica plantada de propósito (e algumas que a
gente plantou sem querer 😬). A lista honesta está lá embaixo em
[Dívida técnica herdada](#dívida-técnica-herdada). Não jogue fora — evolua.

> ⚠️ **Status:** experimental. NÃO usar em produção. NÃO subir exposto.
> Os dados em `data/` são **sintéticos** (ver `data/AVISO-DADOS-SINTETICOS.md`).

---

## O que tem aqui

```
src/scoring.py      # miolo: parse_cv, score_heuristico, avaliar_com_llm, match_score
app.py              # API FastAPI — POST /score
ui.py               # UI Streamlit do recrutador (chama a API)
tests/              # pytest, roda OFFLINE (LLM mockado, sem chave/rede)
data/cvs-exemplos/  # 5 CVs sintéticos
data/vagas/         # 1 vaga (AI Engineer Pleno)
docs/               # notas do time de Data, roadmap das 12 semanas, rascunho de ética
notebook-skeleton.ipynb  # o original, mantido pra referência
```

Como funciona o score (igualzinho ao notebook):

```
score_final = 0.4 * score_heuristico + 0.6 * score_llm
```

- **score_heuristico**: overlap entre as skills do CV e as `skills_obrigatorias`
  da vaga. Determinístico, simples (e ingênuo — ver dívida).
- **score_llm**: um GPT pequeno dá uma nota 0-100 + uma justificativa curta.
  A justificativa é **post-hoc** (gerada depois pelo modelo) — não é explicação
  fiel, não trate como laudo.

Provedor: **OpenAI, um GPT pequeno** (trocamos de um GPT grande pra cortar ~10x de
custo). Dá pra trocar pro **Anthropic, um modelo Claude pequeno** — ver comentário em
`src/scoring.py` (`_chamar_llm`).

---

## Como rodar

Precisa de Python 3.11+ (testamos no 3.14).

**1. Ambiente + deps**

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

**2. Chave da OpenAI** (só pra rodar app/ui de verdade — os testes NÃO precisam)

```bash
cp .env.example .env   # depois edite o .env e coloque sua OPENAI_API_KEY
```

> O código carrega a chave de `os.environ`. Se você usa `.env`, exporte as
> variáveis antes (ex.: `python-dotenv`, ou rode com a var no ambiente). Sim,
> isso podia ser mais redondo — é dívida (ver abaixo).

**3. Sobe a API** (terminal 1)

```bash
uvicorn app:app --reload
# API em http://localhost:8000  | docs interativas em http://localhost:8000/docs
```

**4. Sobe a UI** (terminal 2, com a venv ativada)

```bash
streamlit run ui.py
# abre no browser; a UI chama a API em http://localhost:8000
```

**Testar a API na unha** (sem UI):

```bash
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"cv_texto":"...cole o texto do CV...","vaga":{"titulo":"AI Engineer Pleno","descricao":"","skills_obrigatorias":["Python","FastAPI","Docker","LLM","PostgreSQL"]}}'
```

---

## Testes

Rodam **offline**: as chamadas de LLM são mockadas (monkeypatch). Não precisa de
`OPENAI_API_KEY` nem de internet.

```bash
pip install -r requirements.txt
pytest -q
```

Resultado esperado: **`7 passed`**. Os testes cobrem a heurística, o `parse_cv`
num CV de exemplo real (extração mockada) e o endpoint `POST /score` via
`fastapi.testclient.TestClient`.

---

## Dívida técnica herdada

Isto aqui é **material de trabalho do desafio** — cada item é uma tarefa sua nas
próximas 12 semanas. A gente NÃO consertou de propósito. Não conserte sem antes
entender o porquê.

1. **Sem autenticação / sem multi-tenant.** A API aceita qualquer requisição.
   Cliente A e cliente B compartilhariam tudo. Hoje, se você subir isso exposto,
   vaza geral. (`app.py`)
2. **Sem log de auditoria (LGPD Art. 20).** Nenhuma triagem é persistida: não dá
   pra dizer quem pediu, qual CV, qual prompt, qual modelo, qual score, quando.
   O Art. 20 exige caminho de revisão humana rastreável — não temos rastro.
   (`src/scoring.py`, `app.py`, `ui.py`)
3. **Viés observado e NÃO mitigado, sem métricas de viés.** O time viu (e
   documentou em `docs/notas-data-team.md`): mulheres e candidatos 50+ tendem a
   pontuar menos; formação em universidade de capital pontua mais que interior;
   currículo escrito em inglês pontua mais. Não há disparate impact ratio, equal
   opportunity difference, nem estratificação. **Investigue antes de qualquer
   deploy.** (`src/scoring.py`)
4. **Sem cache.** Reenviou o mesmo CV? Paga o LLM de novo, toda vez. Nada de
   memoização, nada de dedupe. Em 10k CVs/mês isso vira custo e latência.
   (`src/scoring.py`)
5. **Segredos lidos crus.** `OPENAI_API_KEY` sai direto de `os.environ`, sem
   cofre, sem rotação, sem validação decente. (`src/scoring.py`, `.env.example`)
6. **Sem observabilidade / sem deploy.** Sem logs estruturados, sem métricas de
   latência/custo/erro, sem alarme de orçamento (o teto é US$ 250/mês p/ 10k
   CVs), sem pipeline de deploy. (tudo)
7. **Dados pessoais tratados de forma solta.** O CV (PII: nome, e-mail,
   telefone, trajetória) entra inteiro no prompt e vai pra OpenAI nos EUA
   (transferência internacional, Art. 33). Sem mascaramento, sem base legal
   documentada, sem retenção definida. Heurística também é frágil: `parse_cv`
   ignora OCR (CV escaneado vira texto vazio em silêncio) e a heurística ignora
   `anos_experiencia_total`. (`src/scoring.py`)

Ver também `docs/o-que-precisa-construir.md` (roadmap completo) e
`docs/politica-etica-rascunho.md` (pontos em aberto pro Comitê de Ética).

---

## TODO (rabiscos nossos)

- [ ] versionar o prompt (hoje tá hardcoded em `src/scoring.py`)
- [ ] medir custo real por CV (estimamos ~US$0,04 num GPT grande; no mini deve cair
      bastante, mas não medimos)
- [ ] escrever o mapa de viés ANTES de deploy (sério)
- [ ] persistência (Postgres/Supabase) + log auditável
- [ ] auth + isolamento por tenant
- [ ] avaliar um modelo Claude pequeno como alternativa de provedor
- [ ] refazer o set de teste balanceado por gênero/idade/região

Boa sorte. 🍀

— Time de Data, TalentoBR (início deste ano)
