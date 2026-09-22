# ADR-001: Adoção da Stack B para o TalentoBR

- **Status:** Aceita
- **Data:** 14/09/2026
- **Decisores:** Equipe de Produto, Engenharia e Dados

## Contexto

O TalentoBR é um produto de apoio à triagem de currículos. Embora o motor de
scoring e a integração com LLM sejam componentes importantes, o valor
operacional do produto acontece na interface utilizada pelo recrutador: upload
do currículo, seleção da vaga, visualização do score e da justificativa,
revisão humana e registro da decisão.

O protótipo atual já possui uma API em FastAPI e uma interface em Streamlit.
Também precisamos de uma opção de deploy que permita validar rapidamente o
fluxo com usuários, mantendo baixo esforço operacional e sem introduzir uma
camada de frontend mais complexa antes da validação do produto.

Foram consideradas alternativas com uma API e frontend web tradicional, como
Next.js, bem como a manutenção de uma solução baseada apenas em notebook. A
solução baseada em notebook não atende ao fluxo de trabalho do recrutador.
Uma aplicação web tradicional oferece mais flexibilidade de longo prazo, mas
tem custo e tempo de implementação maiores para a fase de validação.

Esta decisão não elimina os riscos apontados na auditoria de segurança,
privacidade, fairness, auditoria, autenticação, cache e observabilidade. A
Stack B é uma decisão de composição tecnológica para o MVP; a entrada em
produção continua condicionada à implementação desses controles.

## Decisão

Adotar a **Stack B**:

- **Backend:** FastAPI, responsável pelos endpoints de scoring, validação de
  contratos, integração com o motor de avaliação e futura aplicação das
  políticas de autenticação, autorização, auditoria e isolamento por tenant.
- **Interface web:** Streamlit, responsável pela experiência visual do
  recrutador, incluindo entrada de dados, apresentação dos resultados e
  interação de revisão humana.
- **Deploy:** Hugging Face Spaces, como plataforma de disponibilização do MVP e
  de validação com usuários, priorizando simplicidade de publicação e
  integração com aplicações de IA.

A interface visual do recrutador é o coração do sistema. Por isso, a escolha
prioriza a velocidade para transformar o protótipo em um fluxo utilizável,
testar a experiência de revisão humana e coletar feedback antes de investir em
um frontend dedicado. FastAPI preserva uma separação clara entre interface e
regras de negócio, permitindo substituir o Streamlit no futuro sem reescrever o
motor de scoring.

O deploy em Hugging Face Spaces deve ser tratado como ambiente de MVP,
desenvolvimento e validação controlada. Dados reais, PII e tráfego externo
somente poderão ser processados após a implementação dos controles de
segurança, privacidade e governança definidos na auditoria.

## Consequências

### Consequências positivas

- Entrega rápida de uma experiência visual centrada no recrutador.
- Baixa complexidade inicial para upload, formulários, resultados e ações de
  revisão humana.
- FastAPI fornece contratos HTTP claros e uma fronteira estável para o domínio,
  facilitando testes e futura evolução da interface.
- Reaproveitamento do código e dos conhecimentos já presentes no protótipo.
- Hugging Face Spaces reduz o esforço inicial de infraestrutura e simplifica a
  demonstração de um produto de IA.
- A separação entre UI e backend permite evoluir a camada visual sem acoplar
  diretamente a interface à lógica de scoring.

### Consequências negativas e riscos

- Streamlit não oferece, por padrão, os recursos de uma aplicação web
  corporativa: autenticação robusta, autorização, multi-tenant, gestão de
  sessão e componentes avançados precisarão ser implementados ou providos por
  uma camada externa.
- Hugging Face Spaces pode não atender requisitos de alta disponibilidade,
  isolamento de dados, residência de dados, escalabilidade previsível e
  controles corporativos de compliance. Esses requisitos devem ser validados
  antes de produção.
- Uma arquitetura inicial com UI e API no mesmo ambiente pode dificultar
  escalabilidade independente, observabilidade e separação de blast radius.
- Streamlit pode exigir retrabalho de frontend caso o produto precise de
  workflows complexos, grande volume de usuários ou experiência altamente
  customizada.
- O deploy simples não resolve os riscos de PII enviada ao LLM, transferência
  internacional, segredos, custo, cache ou viés algorítmico.
- A dependência de uma plataforma externa cria risco de lock-in e exige um
  plano de migração para infraestrutura sob controle da organização.

### Mitigações e critérios para evolução

1. Manter o backend com contratos e regras de negócio independentes da camada
   Streamlit.
2. Adicionar autenticação, autorização por tenant, rate limiting, gestão de
   segredos, logs estruturados, métricas e trilha de auditoria antes de
   qualquer exposição a dados reais.
3. Usar persistência externa protegida e não depender do filesystem efêmero do
   ambiente de deploy para currículos ou registros de triagem.
4. Definir limites de custo, cache, idempotência e alertas para chamadas ao
   LLM.
5. Reavaliar a Stack B quando houver requisitos de escala, disponibilidade,
   compliance ou personalização que superem suas capacidades. Nesse momento,
   FastAPI pode ser mantido como backend e a interface pode migrar para um
   frontend dedicado.
