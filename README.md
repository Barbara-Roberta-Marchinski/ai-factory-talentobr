# TalentoBR — CV Screener

Sistema de apoio à triagem de currículos composto por uma API FastAPI e uma
interface web Next.js exportada como site estático.

> **Dados de demonstração:** currículos e vagas em `data/` são sintéticos.
> Não use currículos reais antes de implementar e validar os controles de
> privacidade, segurança, auditoria e conformidade descritos em `docs/`.

## 🚀 Acesso ao Sistema:

https://talentobr-web.onrender.com/

## 🎯 Problema e Solução

**O Problema:** O processo de recrutamento tradicional exige que a equipe de RH invista dezenas de horas na triagem manual de currículos, o que gera gargalos operacionais, atrasa o tempo de contratação e resulta em avaliações iniciais sem padronização.

**A Solução:** O TalentoBR reduz o tempo gasto pelo RH na triagem manual, padronizando a avaliação inicial. O sistema automatiza a leitura e a extração de dados, gerando um *score* de aderência da vaga (híbrido entre heurística e LLM). Ele não substitui o recrutador, mas atua como uma ferramenta de apoio para que a equipe foque seu tempo na revisão humana qualificada.


## Arquitetura

- `app.py`: API FastAPI (`GET /health`, `POST /score`).
- `src/scoring.py`: extração e avaliação com LLM mais score heurístico.
- `talentobr-web/`: frontend Next.js + Tailwind, gerado como export estático
  para hospedagem como Static Site no Render.
- `tests/`: testes pytest da API e do scoring.

O frontend envia o currículo e os dados da vaga diretamente à API. Currículos
PDF com camada de texto são extraídos localmente no navegador; OCR ainda não
está disponível. Consulte [`talentobr-web/README.md`](./talentobr-web/README.md)
para configurar desenvolvimento e deploy no Render.

Na interface, o botão **Carregar vaga** aceita arquivos TXT: a primeira linha
preenche o título e o restante a descrição. Uma seção explícita
`Competências obrigatórias`, `Skills obrigatórias` ou `Tecnologias obrigatórias`
com itens separados por vírgula também preenche as skills da vaga; sem ela, as
skills devem ser informadas manualmente.

## Pré-requisitos

- Python 3.11 ou superior
- Node.js 20 ou superior

## Executar localmente

### API FastAPI

Na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure `ANTHROPIC_API_KEY` em `.env` e inicie a API:

```powershell
uvicorn app:app --reload
```

A API fica disponível em `http://localhost:8000`. A origem local do frontend,
`http://localhost:3000`, é permitida por padrão; para outros domínios, configure
`FRONTEND_ORIGINS` com as origens exatas separadas por vírgulas.

### Frontend Next.js

Em outro terminal:

```powershell
Set-Location talentobr-web
npm ci
Copy-Item .env.example .env.local
npm run dev
```

O `.env.local` do frontend deve conter `NEXT_PUBLIC_API_BASE_URL`, por padrão
`http://localhost:8000`. Acesse `http://localhost:3000`.

## Testes e build estático

```powershell
# Na raiz: testes offline da API e do scoring
.\.venv\Scripts\pytest.exe -q

# Em talentobr-web: lint e export estático (gera talentobr-web/out/)
npm run lint
npm run build
```

No Render, publique `talentobr-web` como Static Site, com o comando de build
`npm ci && npm run build` e diretório publicado `out`. Defina
`NEXT_PUBLIC_API_BASE_URL` no serviço estático e `FRONTEND_ORIGINS` no serviço
da API.

## Scoring

O score final combina a heurística de skills (40%) e a avaliação LLM (60%).
Ele é apenas um insumo para revisão humana e não deve ser usado como decisão
automática de contratação.

## ⚠️ Limitações Conhecidas e Dívida Técnica (Para a Etapa 2)
Este repositório encontra-se na **Fase 1 (Deploy Inicial)** e herdou algumas dívidas técnicas do protótipo v0.4 que serão sanadas na Fase 2:
* **LGPD e Dados Pessoais:** O modelo atual não sanitiza PII (Identificadores Pessoais) antes de enviar ao LLM, o que configura transferência internacional de dados sem base legal formalizada.
* **Auditoria (Art. 20 LGPD):** Atualmente, as triagens e avaliações do LLM não são persistidas em banco de dados, inviabilizando o direito à revisão humana e a rastreabilidade das decisões[cite: 12].
* **Viés Algorítmico:** Testes preliminares do Data Team apontaram tendências de pontuação menor para perfis femininos, candidatos 50+ e regiões fora de capitais. Métricas de *fairness* serão implementadas antes de qualquer operação real[cite: 12].
* **Aviso de Dados:** Todos os currículos na pasta `data/cvs-exemplos/` são **estritamente sintéticos** e gerados para fins de validação.