# Notas — Passagem de Bastão (Time de Data)

> **Contexto de Governança:** Anotações cruas herdadas do time de Data Science sobre o protótipo v0.4 do TalentoBR. Este documento serve como linha de base diagnóstica para os problemas de viés, LGPD (Art. 20) e métricas que devem ser mitigados na Fase 2 do projeto.

---

## Performance Inicial (Legado v0.4)

- Acurácia em set de teste: **76% de match com decisão humana** (concordância em "passar para próxima fase" vs. "descartar").
- Testado com apenas **100 CVs** — sem generalização comprovada e sem balanceamento por área ou senioridade.
- Ausência de curva ROC, matriz de confusão estratificada e testes fora da amostra de treino.

## Observações Qualitativas (Vieses Críticos Identificados)

- **Viés de Gênero e Idade:** Constatado que mulheres e candidatos com 50+ anos tendem a pontuar menos.
- **Viés Geográfico:** Currículos com formação em universidades federais de capitais pontuam mais do que trajetórias equivalentes do interior.
- **Viés de Idioma:** Resumos e currículos escritos em inglês pontuam acima do mesmo perfil descrito em português, indicando artefato de prompt.

## Lacunas Técnicas Conhecidas

- **Explicabilidade:** A justificativa atual é gerada pelo próprio LLM de forma *post-hoc*, não sendo uma explicação causal fiel.
- **Persistência e Arquitetura:** O modelo original rodava inteiramente em memória (notebook), sem persistência de decisões, sem API desacoplada e sem isolamento multi-tenant.
- **Custo e Observabilidade:** Estimativa inicial de ~US$ 0,04 por currículo, sem telemetria em produção ou controle de orçamento.

## Próximos Passos (Transição para a Etapa 2)

- Refazer o conjunto de teste com balanceamento rigoroso por gênero, faixa etária e região.
- Implementar métricas formais de *fairness* (como *disparate impact ratio* e *equal opportunity difference*).
- Mitigar o viés e garantir a conformidade com o Art. 20 da LGPD (direito à revisão humana) antes de escalar a operação.

— Time de Data, TalentoBR (Legado v0.4)