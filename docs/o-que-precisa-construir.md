# O que precisa construir — Roadmap do Desafio

Este documento resume o escopo das 12 semanas para quem está pegando o projeto. Não é uma lista exaustiva — é um mapa do território.

**Status:** Fase 1 (Deploy e Estruturação) concluída. O projeto avança para a Fase 2 (LGPD, Sanitização de PII e Governança).

## 1. Transformar notebook em sistema usável

- [x] Concluído na Etapa 1: API FastAPI e frontend Next.js estão em produção no Render. A interface tem URL pública: https://talentobr-web.onrender.com/. O recrutador pode enviar currículo e vaga, consultar score e justificativa e registrar sua decisão na interface.

## 2. Persistência de decisões

Banco de dados (sugestão: Postgres via Supabase). Tabelas mínimas: `tenants`, `users`, `vagas`, `candidatos`, `cvs`, `triagens`, `decisoes_recrutador`. Cada triagem persiste: input, output, modelo, versão de prompt, timestamp, operador.

## 3. Auth multi-tenant

Cliente A (uma fintech) **não pode em hipótese alguma** ver dados de cliente B (um varejista). Isolamento por `tenant_id` em todas as queries, RLS no banco, auth com escopo. Auditar isso é parte do trabalho.

## 4. Log auditável (Art. 20 LGPD)

Toda decisão precisa ser rastreável. Se um candidato pedir revisão, a TalentoBR precisa conseguir mostrar: o que entrou, o que o modelo respondeu, quem decidiu, em que momento, com qual versão. Log **imutável** (append-only). Sugestão: Langfuse ou tabela dedicada + WORM storage.

## 5. Análise de viés (métricas explícitas)

Implementar métricas: **disparate impact ratio**, **equal opportunity difference**, ao menos por gênero (inferido com cuidado) e faixa etária. Dashboard de viés. Alerta quando métrica cruza threshold.

## 6. APOIO, não SUBSTITUTO

UI desenhada para que o recrutador **decida**, com IA como insumo. Sem auto-rejeição. Botão "discordo do score" obrigatório. Justificativa humana registrada.

## 7. Mapa LGPD detalhado

Quais dados pessoais aparecem em CVs? Quais são sensíveis (Art. 5º, II)? Base legal (Art. 7º)? Retenção? Anonimização para treino? Documento formal para o DPO.

## 8. Transferência internacional

O uso da API da Anthropic pode envolver transferência internacional; confirmar regiões de processamento e retenção contratadas. Implicações do Art. 33 LGPD. Avaliar: cláusulas contratuais padrão, alternativa com data residency BR, ou consentimento específico.

## 9. Pitch para o Comitê de Ética

Apresentação final: o que foi construído, como o viés é monitorado, como o Art. 20 é respeitado, qual o plano de contingência.

## 10. Deploy + observabilidade + custo

- [x] Deploy automatizado via GitHub Actions, com acionamento do deploy no Render a cada push em `main`, e URL pública funcional: https://talentobr-web.onrender.com/. Observabilidade, métricas de latência/custo/taxa de erro, alertas de orçamento e suporte multi-tenant continuam pendentes.

---

**Ordem sugerida:** 1 → 3 → 2 → 4 → 6 → 5 → 7 → 8 → 10 → 9.
