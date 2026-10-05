# ADR-002: Adoção do Render como plataforma de hospedagem PaaS para API FastAPI e Frontend Next.js

## Status
Aceito — 2026-10-04

## Contexto
O projeto TalentoBR foi evoluído de um protótipo em notebook isolado para uma arquitetura desacoplada (Stack B2), composta por um backend em **Python/FastAPI** (`app.py`) responsável pela heurística e orquestração com a API da Anthropic, e um frontend em **Next.js** exportado como site estático[cite: 5]. 

Para atender aos requisitos da Etapa 1, precisávamos selecionar uma plataforma de hospedagem PaaS que fornecesse URLs públicas estáveis, suporte a CI/CD e baixo custo operacional. As diretrizes sugeriam alternativas comuns do mercado como o **Hugging Face Spaces** e a **Vercel**. Era necessário avaliar essas opções e justificar a escolha técnica.

## Decisão
Adotar o **Render** como a plataforma PaaS unificada para hospedar o Web Service da API FastAPI e o Static Site do frontend Next.js.

## Alternativas Consideradas e Descartadas

1. **Hugging Face Spaces (Descartado após falhas de build e erros opacos):**
   * *Motivo do descarte:* Embora seja amplamente sugerido para demonstrações simples baseadas em Streamlit ou Gradio, testes práticos extensivos esbarraram em barreiras intransponíveis de infraestrutura. A plataforma apresentou erros de *build* opacos ("fantasmas") durante o empacotamento e a execução do container, persistindo mesmo após múltiplas reconfigurações e recriação de contas. A ausência de logs diagnósticos claros impediu a resolução do problema. Adicionalmente, o Hugging Face Spaces sofre de suspensão automática (*sleep*) após 48 horas de inatividade, o que inviabiliza uma API web de resposta imediata sem custos.

2. **Vercel (Descartado para o backend):**
   * *Motivo do descarte:* Pelas minhas pesquisas, fiquei insegura quanto aos custos, explicação mais técnica: A Vercel é a referência de mercado para hospedagem de aplicações Next.js. Contudo, para rodar o backend em Python, a Vercel exige o uso de Funções Serverless (*Serverless Functions*), o que impõe um limite estrito de *timeout* (10 segundos no plano gratuito). Como o processamento de currículos com extração de texto e chamadas ao LLM Claude da Anthropic pode oscilar em termos de latência, o modelo de Web Service persistente do Render atende melhor à execução do FastAPI.

3. **Railway:**
   * *Motivo do descarte:* Embora seja uma excelente opção PaaS com suporte nativo a Docker e Python, a plataforma encerrou seu *free tier* permanente, operando sob um modelo de créditos de US$ 5/mês. O Render ofereceu uma alternativa viável dentro do orçamento de custo zero para demonstrações e portfólio.

## Consequências

* **Positivas:**
  * Flexibilidade para hospedar o backend Python (como Web Service persistente) e o frontend (como Static Site 100% gratuito e sem limite de *sleep* nas páginas estáticas).

  * Facilidade na configuração de variáveis de ambiente segregadas (`ANTHROPIC_API_KEY` na API e `NEXT_PUBLIC_API_BASE_URL` no frontend).

  * Simplicidade no controle de CORS através da variável `FRONTEND_ORIGINS`.

* **Negativas:**
  * O plano gratuito do Web Service (API) no Render entra em modo de repouso (*sleep*) após 15 minutos sem requisições, gerando uma latência de 30 a 90 segundos no primeiro acesso do dia, o que exige um aquecimento prévio (*warm-up*) antes de avaliações ao vivo.