# Política de Ética em IA — TalentoBR

**Versão draft 0.3 — a aprovar pelo Comitê**
**Documento interno — Comitê de Ética em IA da TalentoBR**
**Última revisão:** fim do ano passado

---

## 1. Propósito

Esta política estabelece os princípios que orientam o desenvolvimento, a implantação e a operação de sistemas de Inteligência Artificial na TalentoBR, em especial os sistemas que apoiam decisões com impacto sobre pessoas candidatas a vagas de emprego.

## 2. Princípios

Adotamos como base os **Princípios da OECD para IA** (2019, revisão 2024) e o arcabouço da LGPD (Lei 13.709/2018), em particular o Art. 20.

### 2.1 Transparência
Toda decisão suportada por IA deve ser explicável a quem é afetado por ela. Recrutadores e candidatos devem poder saber, em linguagem clara, que critérios foram considerados.

### 2.2 Fairness (justiça)
Os sistemas não devem perpetuar nem amplificar vieses históricos de gênero, raça, idade, origem geográfica, deficiência, orientação sexual ou classe social.

### 2.3 Accountability (prestação de contas)
A TalentoBR é responsável pelas decisões de seus sistemas. Toda decisão automatizada ou semi-automatizada deve ser rastreável a uma versão de modelo, prompt, dado de entrada e identidade de operador.

### 2.4 Human-in-the-loop
**Compromisso central:** toda decisão de triagem produzida por IA na plataforma TalentoBR é **APOIO** à pessoa recrutadora. Em nenhuma hipótese o sistema substitui o julgamento humano sobre prosseguir, descartar ou rever um candidato.

## 3. Conformidade com a LGPD

### 3.1 Art. 20 — Revisão de decisões automatizadas
> "O titular dos dados tem direito a solicitar a revisão de decisões tomadas unicamente com base em tratamento automatizado..."

A TalentoBR garante que:
- Nenhuma decisão final de triagem é "unicamente automatizada" — sempre há mediação humana.
- Candidatos têm canal para solicitar revisão e explicação.
- *(TODO: definir SLA do canal de revisão — sugestão 15 dias úteis, a confirmar com Jurídico)*

### 3.2 Dados sensíveis
Currículos podem conter, de forma indireta, dados pessoais sensíveis (origem racial via foto, religião via instituição de ensino, condição de saúde via afastamentos). *(TODO: protocolo de detecção e mascaramento)*

## 4. Pontos não-resolvidos

> Esta seção lista questões em aberto que precisam ser endereçadas antes da aprovação final desta política.

- **TODO — Viés de gênero:** definir métricas (disparate impact ratio, equal opportunity difference) e thresholds aceitáveis. Quem audita? Com que frequência?
- **TODO — Viés de idade:** o sistema atual pondera "anos de experiência" — isso correlaciona com idade. Como mitigar sem perder sinal legítimo?
- **TODO — Viés geográfico:** CEP, cidade, estado de formação são proxies fortes para classe social. Política de mascaramento?
- **TODO — Auditabilidade:** formato, retenção e acesso ao log de decisões. Quem pode consultar? Por quanto tempo guardamos?
- **TODO — Direito à revisão:** desenho operacional do fluxo Art. 20. Botão na UI do recrutador? Canal externo para candidato?
- **TODO — Transferência internacional:** uso de OpenAI implica transferência para EUA. Avaliar base legal (Art. 33 LGPD), cláusulas-padrão, ou migração para provedor com data residency BR.
- **TODO — Comunicação ao candidato:** o candidato sabe que seu CV está sendo pontuado por IA? Onde isso aparece?

## 5. Governança

Comitê de Ética em IA — composto por: Diretoria de Plataforma, DPO, Jurídico, Recrutamento, Diversidade & Inclusão, representante externo (acadêmico).

Reuniões trimestrais. Decisões registradas em ata pública interna.

---

*Documento em construção. Comentários para `etica-ia@talentobr.com.br`.*
