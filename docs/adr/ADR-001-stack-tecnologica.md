# ADR-001: Evolução da Stack B (Migração para Next.js e Render)

- **Status:** Aceita
- **Data:** Outubro de 2026
- **Decisores:** Equipe de Engenharia e Produto (AI Factory)

## Contexto

O TalentoBR é um produto de apoio à triagem de currículos. O protótipo herdado da equipe de Data validou o motor de scoring (Heurística + LLM) utilizando uma API em FastAPI e uma interface básica em Streamlit.

Embora o Streamlit tenha sido útil para a prototipagem rápida, a visão de produto exige uma interface "SaaS B2B profissional", com tratamento de estado complexo, feedback visual elegante (tratamento de erros da API da Anthropic sem quebrar a tela) e um dashboard de resultados responsivo. Além disso, precisamos de uma opção de deploy no *free tier* que minimize o impacto do *cold start* (tempo de despertar do servidor) para o usuário final.

Esta decisão foca na evolução da camada de apresentação (Stack B2) e infraestrutura. Ela não elimina os riscos apontados na auditoria inicial (falta de autenticação, vazamento de PII para o LLM, ausência de banco de dados e viés não mitigado). A entrada em produção definitiva continua condicionada à implementação desses controles.

## Decisão

Evoluir a arquitetura para uma **Stack B2 customizada**:

- **Backend (Mantido):** FastAPI. Preserva a lógica de inteligência artificial em Python, os endpoints de scoring e a integração com o motor de avaliação, além de centralizar as futuras políticas de autenticação e isolamento por tenant.
- **Interface Web (Nova):** Next.js (React) + Tailwind CSS. O Streamlit foi descartado. O Next.js será configurado com `output: 'export'` para gerar um site 100% estático (Static Site Generation).
- **Deploy (Novo):** Render. O backend rodará como um *Web Service* (sujeito a sleep mode no free tier), enquanto o frontend rodará como um *Static Site* (sem sleep mode, hospedagem global e gratuita).

A interface visual do recrutador é o coração do sistema. A separação estrita entre um frontend React estático e uma API Python garante que o recrutador acesse a tela instantaneamente, mascarando qualquer lentidão do backend com componentes visuais de carregamento (*spinners*).

## Consequências

### Consequências positivas

- **Experiência de Usuário (UX):** Entrega de uma interface SaaS rica, em duas colunas, aderente aos padrões de mercado B2B.
- **Performance de Frontend:** Como o site é estático e hospedado no Render, o carregamento inicial da página é instantâneo (zero *cold start* na interface).
- **Desacoplamento Tecnológico:** FastAPI fornece contratos HTTP claros (JSON). O frontend React não conhece a lógica do LLM, apenas consome o serviço, facilitando testes e manutenção.
- **Governança de Custos:** Ambas as pontas (API e Frontend) estão hospedadas na mesma plataforma (Render) com custo zero na fase de MVP.

### Consequências negativas e riscos

- **Complexidade Operacional:** A equipe agora precisa manter e fazer o deploy de duas aplicações distintas (Node.js/React e Python/FastAPI), aumentando a carga cognitiva.
- **Gestão de CORS:** Frontend e Backend rodam em origens diferentes, exigindo configuração estrita de `CORSMiddleware` na API para evitar bloqueios do navegador.
- **Cold Start do Backend:** No free tier do Render, a API do FastAPI "dormirá" após 15 minutos. O primeiro currículo enviado no dia poderá levar até 50 segundos para ser processado enquanto a máquina acorda.
- **Limitações do Static Export:** Ao exportar o Next.js estaticamente, perdemos recursos nativos de servidor do framework (como *Server Actions* e otimização de imagens dinâmica).

### Mitigações e critérios para evolução

1. Configurar o `CORSMiddleware` no FastAPI liberando inicialmente origens locais e, posteriormente, travando apenas para a URL oficial do frontend no Render.
2. Implementar estados de *loading* robustos na interface React para educar o usuário a aguardar o *cold start* da API sem abandonar a página.
3. Adicionar persistência externa (ex: Supabase/PostgreSQL) e autenticação antes de qualquer exposição a dados reais de candidatos, para cumprir o Art. 20 da LGPD (trilha de auditoria).
4. Migrar o backend para um plano pago (always-on) assim que o volume de uso do RH inviabilizar o tempo de espera do *sleep mode*.