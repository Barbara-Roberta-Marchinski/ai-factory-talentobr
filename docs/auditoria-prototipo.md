# Auditoria de Dívidas Técnicas — Protótipo TalentoBR

**Data da auditoria:** 14/09/2026  
**Escopo:** `app.py` e `src/scoring.py`, complementados pelo contexto técnico do
protótipo e pelas dívidas já registradas pelo time de Data.  
**Classificação:** o sistema é experimental e não deve ser exposto nem utilizado
em produção até que os controles abaixo sejam implementados e validados.

## Resumo executivo

O protótipo combina uma heurística de sobreposição de skills com uma avaliação
de LLM:

```text
score_final = 0,4 * score_heuristico + 0,6 * score_llm
```

O fluxo atual recebe o currículo bruto em `POST /score`, envia esse conteúdo a
um provedor externo para extração e depois envia os campos estruturados
novamente para avaliação. Não há autenticação, isolamento por cliente,
persistência, auditoria, cache, métricas operacionais ou proteção adequada de
segredos.

Essas lacunas não são apenas melhorias de engenharia. Elas afetam diretamente:

- conformidade com a LGPD e a capacidade de contestação/revisão humana;
- tratamento justo de candidatos e evidências para compromissos ESG;
- custo, latência e previsibilidade do orçamento;
- confidencialidade dos currículos e separação entre clientes;
- segurança da credencial que autoriza chamadas pagas ao provedor de LLM.

## 1. Viés algorítmico não mitigado

### Descrição do Problema

O comportamento observado pelo time de Data indica que o modelo penaliza
currículos de mulheres e de candidatos com mais de 50 anos, favorece formações
em instituições localizadas em capitais e pontua melhor currículos escritos em
inglês. O próprio código registra que esse viés observado no notebook
“continua aqui” e não foi mitigado.

O risco é ampliado pelo desenho atual:

- `avaliar_com_llm` envia o candidato inteiro, incluindo trajetória, formação e
  linguagem do currículo, para um julgamento em texto livre;
- a nota do LLM tem peso de 60% no resultado final;
- não há remoção ou tratamento de atributos sensíveis e proxies, como nome,
  idioma, idade inferida por datas de formação/experiência ou localização da
  instituição;
- os pesos `PESO_HEURISTICA = 0.4` e `PESO_LLM = 0.6` são fixos e não possuem
  justificativa baseada em validação;
- não existem métricas de fairness, conjunto de teste balanceado, análise por
  grupo, limiares de alerta ou processo de revisão de impacto.

Consequentemente, a justificativa produzida pelo LLM é apenas post-hoc: ela não
prova que os fatores apresentados causaram a pontuação e não substitui uma
explicação auditável.

### Impacto no Negócio/Custos

- **Risco de discriminação:** candidatos qualificados podem ser eliminados ou
  rebaixados por atributos protegidos ou por proxies indevidos.
- **Risco regulatório e reputacional:** decisões inconsistentes podem gerar
  reclamações, investigações, ações judiciais e perda de confiança de
  candidatos, clientes e parceiros.
- **Risco comercial:** clientes corporativos não conseguirão demonstrar que o
  produto atende seus compromissos de diversidade, equidade e inclusão.
- **Relatórios ESG incompletos:** sem métricas como *disparate impact ratio*,
  *selection rate* por grupo, *equal opportunity difference* e taxas de
  falso positivo/falso negativo, não há evidência quantitativa para auditorias
  ESG nem para acompanhamento de metas.

### Recomendação de Correção

1. Suspender qualquer decisão automatizada e manter o resultado explicitamente
   como apoio à decisão humana, com revisão obrigatória e possibilidade de
   discordância registrada.
2. Definir um mapa de atributos protegidos e proxies, documentar a finalidade
   de cada variável e construir um conjunto de validação representativo por
   gênero, faixa etária, região/localização da formação e idioma.
3. Medir antes de cada release as taxas de seleção por grupo, *disparate
   impact ratio*, *equal opportunity difference*, precisão e recall. Definir
   limiares de bloqueio, responsável pela aprovação e plano de remediação.
4. Separar a avaliação de competências da identidade do candidato: aplicar
   minimização/anonimização para o scoring quando possível, neutralizar idioma
   e localização como sinais indevidos e validar que a normalização não remove
   evidência profissional legítima.
5. Comparar o desempenho com uma linha de base determinística e fazer testes
   contrafactuais (mesmo currículo com alteração controlada de nome, idade,
   idioma e instituição). Versionar prompt, modelo, pesos e conjunto de dados,
   mantendo os resultados de fairness para auditoria.

## 2. Violação da LGPD (Art. 20) e tratamento de PII

### Descrição do Problema

O endpoint `POST /score` recebe `cv_texto` bruto. `extrair_campos` interpola o
texto completo diretamente no prompt, e `avaliar_com_llm` envia ao LLM os campos
estruturados que incluem nome, e-mail, formação e experiência. Assim, dados
pessoais e potencialmente sensíveis entram crus no provedor externo, sem
mascaramento, minimização ou classificação prévia. O fluxo também representa
transferência internacional de dados para a OpenAI, sem que o código evidencie
base legal, mecanismo contratual, finalidade, retenção ou governança para essa
transferência.

Nenhuma etapa da API ou do scoring persiste a solicitação, o prompt, o modelo,
as versões, o resultado ou a decisão do recrutador. Não existe log de
auditoria nem banco de dados para reconstruir quem solicitou a triagem, quando,
com qual vaga e qual versão do sistema. Isso inviabiliza o rastreio necessário
para revisão humana, contestação e demonstração de conformidade com o Art. 20.

### Impacto no Negócio/Custos

- Impossibilidade de explicar, reproduzir e revisar uma triagem contestada.
- Perda de evidência sobre intervenção humana, versão do modelo e fundamento
  usado na decisão.
- Exposição de PII a um terceiro e risco de uso além da finalidade declarada,
  retenção indevida ou transferência internacional sem controles adequados.
- Potenciais incidentes de segurança, notificações, sanções, custos jurídicos e
  suspensão de contratos com clientes que exigem governança de dados.
- Sem retenção e trilha de auditoria, também não é possível atender de forma
  confiável solicitações de titulares, correções, eliminação ou investigação de
  incidentes.

### Recomendação de Correção

1. Fazer *privacy by design*: classificar os campos, coletar somente o
   necessário para a finalidade de matching, separar identificadores da análise
   e mascarar nome, e-mail, telefone, endereço, links e outros identificadores
   antes de qualquer chamada ao LLM.
2. Formalizar com Jurídico/DPO a base legal, a finalidade, os prazos de
   retenção, os direitos dos titulares, a transferência internacional e os
   contratos/garantias aplicáveis ao provedor. Configurar o provedor para não
   usar os dados para treinamento quando essa opção estiver disponível.
3. Criar persistência protegida e um registro imutável/auditável por triagem,
   contendo identificador do tenant e do solicitante, timestamp, hash do CV,
   vaga, versão do prompt/modelo, entradas minimizadas, scores, justificativa,
   revisão humana, decisão final e motivo de eventual override.
4. Criptografar dados em trânsito e em repouso, restringir acesso por função,
   aplicar retenção/eliminação automática e registrar acessos aos dados.
5. Implementar um fluxo de revisão humana e contestação que consulte esse
   registro sem reexpor o CV bruto ao LLM. Testar mascaramento com dados
   sintéticos e casos de PII adversaria antes de liberar o serviço.

## 3. Ausência de cache e observabilidade

### Descrição do Problema

Cada chamada a `POST /score` executa novamente `extrair_campos` e
`match_score`; dentro dele, `avaliar_com_llm` realiza outra chamada ao LLM.
Não há cache, deduplicação por conteúdo, idempotência ou reaproveitamento de
resultados. Reenviar o mesmo currículo para a mesma vaga, inclusive por
retries do cliente, gera novas chamadas pagas.

Também não há logs estruturados, métricas de latência, contagem de tokens,
custo por chamada, taxa de erro, uso por tenant, saturação ou alarmes de
orçamento. O código não fornece meios para saber se uma resposta veio de uma
nova avaliação, medir o custo real ou interromper o consumo quando o teto for
atingido.

O README estima aproximadamente US$ 0,04 por currículo no modelo maior. Mesmo
usando essa referência conservadora, 10.000 currículos representam cerca de
US$ 400, acima do teto mensal de US$ 250; o fluxo atual pode consumir mais,
pois há duas etapas de LLM por currículo e não há deduplicação.

### Impacto no Negócio/Custos

- O teto de US$ 250/mês para 10 mil currículos não é previsível nem
  controlável.
- Retries e reprocessamentos podem gerar cobrança duplicada, aumento de
  latência e experiência inconsistente para o recrutador.
- Sem métricas, incidentes de custo, degradação ou qualidade podem permanecer
  invisíveis até a fatura ou uma reclamação do cliente.
- A operação não consegue estabelecer SLA, calcular custo unitário nem
  dimensionar capacidade para crescimento.

### Recomendação de Correção

1. Introduzir cache com chave derivada de hash criptográfico do conteúdo
   normalizado do CV, da vaga, do prompt versionado, do modelo e dos parâmetros
   relevantes. Não usar PII como chave nem expor o conteúdo no cache.
2. Persistir separadamente a extração e o score, com TTL, invalidação explícita
   quando o prompt/modelo mudar e controle de concorrência para evitar chamadas
   duplicadas simultâneas.
3. Adotar idempotency key por solicitação e retries limitados com backoff,
   distinguindo erros transitórios de erros permanentes.
4. Instrumentar logs estruturados e métricas para latência, tokens de entrada e
   saída, custo estimado/real, cache hit ratio, erros, volume por tenant e
   distribuição dos scores. Remover PII dos logs.
5. Criar alertas e um *budget guardrail*: orçamento diário/mensal, limite por
   tenant, circuito de bloqueio/degradação e painel operacional. Validar o
   desenho com uma simulação de 10 mil currículos para demonstrar margem dentro
   do teto.

## 4. Falta de autenticação e multi-tenant

### Descrição do Problema

O `app.py` expõe `POST /score` sem autenticação, autorização, rate limit ou
identificação de tenant. Qualquer requisição que alcance a porta pode enviar
currículos para processamento. Não há escopo de cliente em `ScoreRequest`,
nenhuma política de isolamento e nenhum controle de acesso por função.

Em um cenário com múltiplos clientes, os dados, custos, limites e registros não
teriam fronteira confiável. A rota `/health` pode permanecer pública para
monitoramento, mas o endpoint de scoring não pode ser tratado como público.

### Impacto no Negócio/Custos

- Qualquer pessoa com acesso à rede pode submeter PII de terceiros e consumir a
  chave da OpenAI, causando vazamento e abuso financeiro.
- Um cliente pode acessar ou inferir dados de outro se a persistência for
  adicionada sem isolamento desde o início.
- Ausência de rate limit facilita negação de serviço, automação abusiva e
  estouro do orçamento.
- Viola requisitos básicos de segurança de clientes corporativos e aumenta o
  impacto de qualquer incidente.

### Recomendação de Correção

1. Colocar a API atrás de gateway privado/TLS e implementar autenticação
   baseada em OIDC/OAuth2 ou chaves por serviço com rotação e expiração.
2. Criar autorização por tenant e função (recrutador, administrador, auditor),
   propagando um `tenant_id` confiável da identidade autenticada, nunca do
   corpo da requisição.
3. Aplicar isolamento lógico e, quando possível, row-level security na
   persistência; testar explicitamente que um tenant não consegue consultar,
   reprocessar ou excluir dados de outro.
4. Adicionar rate limit, quotas e limites de tamanho de payload por tenant,
   além de proteção contra abuso e validação de origem no frontend.
5. Cobrir autenticação, autorização negativa, isolamento, limites e expiração
   de credenciais com testes de integração antes de qualquer exposição externa.

## 5. Segredos expostos

### Descrição do Problema

`_get_client` lê `OPENAI_API_KEY` diretamente de `os.environ` e a entrega ao
cliente da OpenAI. O próprio código reconhece que não há cofre de segredos,
rotação ou validação adequada. A mensagem de erro orienta a criação de um
`.env`, o que é aceitável apenas como conveniência local e não como mecanismo
de produção.

Não há evidência no fluxo de escopo mínimo da chave, rotação automática,
auditoria de uso ou bloqueio de exposição em logs e ambientes de
desenvolvimento. Como a API também não tem autenticação, uma chave válida
ficaria atrás de uma superfície de abuso ampla.

### Impacto no Negócio/Custos

- Vazamento da chave permite chamadas indevidas, aumento imediato da fatura e
  possível acesso a outros recursos vinculados à conta do provedor.
- Revogar manualmente uma credencial compartilhada interrompe ambientes e
  dificulta identificar a origem do abuso.
- Segredos em `.env`, logs, dumps ou pipelines podem persistir fora do controle
  da organização e ampliar o raio de impacto de um incidente.

### Recomendação de Correção

1. Usar um secret manager gerenciado (por exemplo, cofre da nuvem ou Vault),
   com acesso por identidade de workload, nunca por segredo embutido no código,
   imagem ou repositório.
2. Criar chaves separadas por ambiente e, quando suportado, por serviço/tenant,
   com escopo mínimo, limites de gasto e permissões mínimas.
3. Rotacionar credenciais automaticamente, revogar a chave atual se houver
   suspeita de exposição e registrar acesso ao segredo sem registrar seu valor.
4. Validar configuração no startup, falhar com erro operacional claro e evitar
   incluir valores de ambiente, prompts ou PII em logs e mensagens de exceção.
5. Integrar secret scanning ao repositório e ao CI, revisar histórico de
   commits e documentar o procedimento de resposta a vazamento.

## 6. Lacunas técnicas adicionais que aumentam o risco

Além dos cinco pontos críticos, o próprio fluxo contém dívidas que devem entrar
no plano de estabilização:

- **Prompt e pesos não versionados:** prompts e os pesos do blend estão
  hardcoded, dificultando reproduzir resultados e medir regressões.
- **Heurística limitada:** a interseção literal de skills ignora sinônimos,
  stemming e `anos_experiencia_total`; isso pode gerar falsos negativos
  independentemente do viés do LLM.
- **OCR ausente e falha silenciosa:** PDFs escaneados podem virar texto vazio
  sem alerta, produzindo uma avaliação inválida.
- **Qualidade da explicação:** a justificativa é gerada depois da nota e não é
  uma explicação causal ou fiel do processo.

Esses itens devem ser tratados com testes de qualidade, validação de entrada,
telemetria e revisão de modelo, sem serem usados para justificar a liberação
antes dos controles de segurança, privacidade e fairness.

## Ordem de implementação recomendada

1. **Bloqueio imediato:** não expor a API; proteger/revogar a chave se houver
   suspeita de vazamento; adicionar autenticação, TLS, rate limit e segregação
   de tenant.
2. **Privacidade e conformidade:** mascarar PII, definir base legal e
   transferência internacional, criar persistência auditável, retenção e
   revisão humana.
3. **Fairness:** construir a base balanceada, medir as métricas por grupo,
   executar testes contrafactuais e aprovar critérios de liberação com Data,
   Jurídico/DPO e Comitê de Ética.
4. **Operação e custo:** implementar cache/idempotência, instrumentação,
   orçamento com circuit breaker e testes de carga com 10 mil currículos.
5. **Qualidade contínua:** versionar prompts/modelos/pesos, acompanhar drift,
   qualidade da extração e fairness, e repetir a auditoria a cada mudança.

O protótipo só deve avançar para produção quando houver evidência verificável
de que cada controle foi implementado, testado e atribuído a um responsável
operacional.
