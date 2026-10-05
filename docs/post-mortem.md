# Post-Mortem: Falha de comunicação entre Frontend e API (Bloqueio de CORS)

**Severidade:** SEV-2 (Bloqueio de funcionalidade principal em produção)  
**Data:** 04/10/2026  
**Status:** Resolvido  

## 1. Resumo do Incidente
Logo após o primeiro deploy bem-sucedido da Stack B2 (FastAPI + Next.js) no Render, o sistema apresentou indisponibilidade silenciosa para o usuário final. Ao tentar submeter um currículo para análise, o frontend não conseguia se comunicar com o backend. A investigação apontou que a API estava bloqueando a requisição por razões de segurança (erro de CORS). O incidente foi mitigado após a configuração correta da variável de ambiente `FRONTEND_ORIGINS` no painel do Web Service.

## 2. Impacto
* **Usuários afetados:** Apenas a equipe de engenharia (ocorreu logo após o *go-live* inicial, antes da liberação para os recrutadores).
* **Transações perdidas:** Nenhuma, mas o fluxo de pontuação de currículos ficou inoperante.

## 3. Linha do Tempo
* **Deploy inicial:** Ambos os serviços (API e Frontend) receberam o selo "Live" no Render.
* **Detecção:** Durante o *smoke test* manual na interface pública, o botão de submissão não retornava o *score*.
* **Diagnóstico:** A inspeção do console do navegador revelou o erro: `Access to fetch at [API_URL] from origin [FRONTEND_URL] has been blocked by CORS policy`.
* **Mitigação:** Acessado o painel do Render da API, adicionada a chave `FRONTEND_ORIGINS` com o valor exato da URL pública do Next.js (sem a barra `/` no final).
* **Resolução:** Após o *rebuild* da API, o sistema normalizou e a comunicação foi restabelecida com sucesso.

## 4. Análise de Causa Raiz (Os 5 Porquês)
Utilizando a técnica dos 5 Porquês para isolar a causa sistêmica:

1. **Por que a interface não conseguiu receber o *score* do currículo?** 
   Porque a requisição HTTP POST foi bloqueada pelo navegador do usuário.
2. **Por que o navegador bloqueou a requisição?** 
   Devido a uma violação da política de CORS (Cross-Origin Resource Sharing), já que o frontend e a API estão hospedados em domínios diferentes no Render.
3. **Por que a API recusou a origem do frontend?** 
   Porque a lista de origens permitidas (allowed origins) no middleware do FastAPI não continha a URL pública de produção do Next.js.
4. **Por que a URL não estava na lista do middleware?** 
   Porque a variável de ambiente `FRONTEND_ORIGINS`, responsável por injetar essa permissão no código, não foi configurada na plataforma antes do primeiro *deploy*.
5. **Causa Raiz:** O checklist de *deploy* e a "Definition of Done" (DoD) da equipe não previam a verificação de variáveis de ambiente exclusivas de produção (como o domínio final do frontend) antes do lançamento. O ambiente local (localhost) mascarou o problema, pois as portas locais costumam ser permitidas por padrão durante o desenvolvimento.

## 5. O que foi bem & O que pode melhorar
* **✓ O que foi bem:** Os logs de erro no console do navegador foram claros e permitiram um diagnóstico em menos de 5 minutos.
* **✗ O que pode melhorar:** A dependência excessiva de que "se funciona no localhost, funcionará na nuvem", ignorando políticas de segurança de rede que só entram em vigor em ambientes distribuídos.

## 6. Itens de Ação
Toda falha deve gerar melhorias sistêmicas com responsáveis e prazos.

| Ação | Responsável | Status |
| :--- | :--- | :--- |
| Configurar a variável `FRONTEND_ORIGINS` com a URL exata do Render na API. | Engenharia | **Concluído** (Mitigação) |
| Documentar no `README.md` a exigência e a formatação exata da variável (explicando que não deve conter barra `/` no final) para futuros *deploys*. | Engenharia | **Concluído** |
| Adicionar a checagem de variáveis de ambiente de produção (Secrets e URLs) no checklist padrão de novos ambientes. | Engenharia | Para a Fase 2 |