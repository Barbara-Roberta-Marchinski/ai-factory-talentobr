# Matriz de Decisão de Stack — TalentoBR

Este documento registra a análise comparativa e o método de escolha da stack tecnológica para o sistema TalentoBR, seguindo as diretrizes de arquitetura e priorização de problemas de negócio.

## 1. Critérios de Avaliação e Pesos
Definidos *antes* da avaliação das opções para garantir imparcialidade:

1. **Adequação à Experiência do Recrutador (UI/UX):** O sistema exige uma interface B2B clara para submissão de currículos/vagas e exibição de dashboards analíticos. *(Peso: 5)*
2. **Controle sobre a Lógica de Scoring (Heurística + LLM):** Necessidade de manipular código Python customizado para processamento de texto, match de skills e montagem de prompts na Anthropic API. *(Peso: 5)*
3. **Flexibilidade e Manutenibilidade do Código:** Facilidade para versionamento em Git, testes automatizados (`pytest`) e pipeline de CI/CD. *(Peso: 4)*
4. **Custo Operacional e Escalabilidade (Tier Gratuito / Low-cost):** Alinhamento com o teto orçamentário inicial e facilidade de hospedagem em provedores PaaS (Render). *(Peso: 4)*
5. **Velocidade de Integração com APIs Externas:** Facilidade de consumo direto da API da Anthropic sem intermediários restritivos. *(Peso: 3)*

---

## 2. Comparativo das Stacks Avaliadas

As opções foram pontuadas de 1 a 5 em cada critério:

| Critério de Decisão | Peso | Stack A (Workflow / n8n) | Stack B2 (App Full-stack / FastAPI + Next.js) | Stack C (Low-code / Make + Airtable) |
| :--- | :---: | :---: | :---: | :---: |
| **1. Adequação à UI/UX** | 5 | Nota 2 *(Foco em fluxo invisível, UI secundária)* | **Nota 5** *(Interface web rica e dedicada para o RH)* | Nota 3 *(Telas engessadas geradas por plataformas low-code)* |
| **2. Controle de Scoring** | 5 | Nota 3 *(Lógica restrita a nós de código no workflow)* | **Nota 5** *(Controle total em Python, FastAPI e scripts de scoring)* | Nota 2 *(Dificuldade de customizar algoritmos complexos de texto)* |
| **3. Flexibilidade e CI/CD** | 4 | Nota 3 *(Versionamento em JSON de workflows)*[cite: 11] | **Nota 5** *(Código nativo em Git, testes unitários e GitHub Actions)* | Nota 2 *(Forte lock-in na plataforma proprietária)* |
| **4. Custo e Escalabilidade** | 4 | Nota 3 *(Custos de execução escalam rápido por operação)* | **Nota 4** *(Hospedagem estática grátis e Web Service eficiente no Render)* | Nota 3 *(Planos baseados em consumo/operações mensais)* |
| **5. Integração com LLM** | 3 | Nota 4 *(Boa integração via requisições HTTP)* | **Nota 5** *(Integração nativa via SDK/API REST oficial da Anthropic)* | Nota 3 *(Dependência de módulos pré-fabricados de IA)* |

---

## 3. Resultado do Scoring (Peso × Nota)

* **Stack A (Workflow - n8n + Railway):** $2\times5 + 3\times5 + 3\times4 + 3\times4 + 4\times3 = 10 + 15 + 12 + 12 + 12 =$ **61 pontos**
* **Stack B2 (Full-stack - FastAPI + Next.js):** $5\times5 + 5\times5 + 5\times4 + 4\times4 + 5\times3 = 25 + 25 + 20 + 16 + 15 =$ **101 pontos** *(Sugerida)*
* **Stack C (Low-code - Make + Airtable):** $3\times5 + 2\times5 + 2\times4 + 3\times4 + 3\times3 = 15 + 10 + 8 + 12 + 9 =$ **54 pontos**

---

## 4. Conclusão e Decisão Final

A **Stack B2 (FastAPI + Next.js)** sagrou-se vencedora com **101 pontos**, demonstrando ser a única arquitetura capaz de atender plenamente à necessidade de uma interface B2B interativa aliada ao processamento de algoritmos customizados de heurística e inteligência artificial (Anthropic Claude), mantendo a governança de código e o pipeline de CI/CD exigidos pelo projeto.