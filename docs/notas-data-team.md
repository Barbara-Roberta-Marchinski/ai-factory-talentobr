# Notas — Data Team

*Anotações cruas do time de Data Science sobre o protótipo v0.4. Não revisado, não polido.*

---

## Performance

- Acurácia em set de teste: **76% de match com decisão humana** (concordância em "passar para próxima fase" vs. "descartar").
- Mas testamos só com **100 CVs** — não generalizou ainda. Set de teste foi construído manualmente em uma tarde, sem balanceamento por área ou senioridade.
- Não temos curva ROC, matriz de confusão estratificada, nem teste em CVs fora da amostra de treino do prompt.

## Observações qualitativas (preocupantes)

- Reparamos que **mulher e candidato de 50+ tendem a pontuar menos**. Não fomos investigar.
- Currículos com formação em universidade federal de capital tendem a pontuar mais que mesma trajetória com formação em interior. Pode ser sinal legítimo (qualidade de curso) ou viés. Não separamos.
- Currículos com inglês "fluente" no resumo escrito em inglês pontuam mais que mesmo perfil descrito em PT. Provável artefato de prompt.

## O que faltou (sabemos)

- Explicabilidade. SHAP não faz muito sentido para LLM. Cogitamos extrair attention weights mas não tivemos tempo. Hoje a "justificativa" é gerada pelo próprio modelo — não é explicação fiel, é post-hoc.
- Persistência. Tudo roda em memória, perde ao fechar o notebook.
- API. Não existe.
- Auth. Não existe. Não é multi-tenant.
- Versionamento de prompt. Hoje o prompt está hardcoded numa célula.
- Custo. Estimamos ~US$ 0.04 por CV com um GPT grande, mas não medimos em produção.

## Próximos passos sugeridos (para quem pegar)

- Refazer set de teste com balanceamento por gênero, faixa etária e região.
- Avaliar modelos menores (um GPT pequeno) — custo cai 10x, qualidade talvez aceitável.
- Investigar viés observado **antes** de qualquer deploy.
- Conversar com Jurídico/DPO antes de qualquer coisa.

— Time de Data, início deste ano
