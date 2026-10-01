---
title: TalentoBR
emoji: 🏢
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: ui.py
pinned: false
---

# TalentoBR — CV Screener

O **TalentoBR CV Screener** é um sistema de apoio à triagem de currículos, desenvolvido para auxiliar recrutadores na análise de aderência entre perfis de candidatos e requisitos de vagas. O produto é composto por uma API RESTful e uma interface de usuário interativa, automatizando a extração de dados e fornecendo um *score* híbrido de recomendação.

> ⚠️ **Status dos Dados:** Os currículos e informações presentes na pasta `data/` são estritamente **sintéticos** e gerados para fins de validação estrutural do sistema.

---

## Arquitetura e Estrutura

O sistema é dividido em dois serviços principais: o motor de processamento (API FastAPI) e a interface do recrutador (UI Streamlit).

*   `src/scoring.py`: Núcleo de regras de negócio, heurísticas de correspondência e orquestração de chamadas ao LLM.
*   `app.py`: Backend em FastAPI que expõe o endpoint `POST /score`.
*   `ui.py`: Frontend em Streamlit para interação do recrutador e revisão humana de resultados.
*   `tests/`: Suíte de testes automatizados via `pytest`.
*   `docs/`: Documentação oficial de governança, arquitetura e auditoria técnica.

## Lógica de Avaliação (Scoring)

O algoritmo de recomendação do TalentoBR utiliza uma abordagem híbrida, combinando determinismo e análise semântica:

`Score Final = (0.4 * Score Heurístico) + (0.6 * Score LLM)`

1.  **Score Heurístico:** Cálculo determinístico baseado na sobreposição exata entre as habilidades extraídas do currículo e os requisitos obrigatórios da vaga.
2.  **Score LLM:** Avaliação qualitativa gerada por inteligência artificial, que analisa o contexto da trajetória do candidato e devolve uma nota de 0 a 100 acompanhada de uma justificativa em texto.

**Provedor de IA:** O sistema utiliza a API da Anthropic, empregando o modelo `claude-3-5-haiku-20241022` via Messages API para processamento rápido e eficiente[cite: 5].

> **Nota de Conformidade (LGPD Art. 20):** O sistema atua estritamente como *apoio* à tomada de decisão. A interface garante o *Human-in-the-loop*, exigindo que o recrutador valide o score e tome a decisão final. A justificativa gerada pelo modelo é pós-hoc e não substitui o julgamento humano.

---

## Como Executar o Projeto Localmente

**Pré-requisitos:** Python 3.11 ou superior.

**1. Configuração do Ambiente Virtual e Dependências**
```bash
python -m venv .venv
# Ativação no Windows:
.venv\Scripts\activate
# Ativação no Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt