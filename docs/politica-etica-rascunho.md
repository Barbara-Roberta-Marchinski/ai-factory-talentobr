# Política de Governança, Ética e LGPD em IA — TalentoBR

**Versão 1.0 — Aprovada e Ativa**
**Documento interno — Comitê de Ética em IA da TalentoBR**
**Última revisão:** 22/10/2026 (Deploy e Conformidade)

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

## 3. Conformidade com a LGPD e Privacidade

### 3.1 Art. 20 — Revisão de decisões automatizadas
> "O titular dos dados tem direito a solicitar a revisão de decisões tomadas unicamente com base em tratamento automatizado..."

A TalentoBR garante que:
- Nenhuma decisão final de triagem é "unicamente automatizada" — sempre há mediação humana.
- Candidatos têm canal para solicitar revisão e explicação.
- *(TODO: definir SLA do canal de revisão — sugestão 15 dias úteis, a confirmar com Jurídico)*

### 3.2 Mapa de Dados e Base Legal (Art. 7º LGPD)
| Ponto de Coleta | Dados Pessoais | Base Legal (LGPD) | Justificativa |
| :--- | :--- | :--- | :--- |
| **Upload de Currículo** | Trajetória e competências | Execução de Contrato (Art. 7º, V) | Avaliação técnica para a vaga. |
| **Sanitização IA** | E-mail, Telefone, CPF | Obrigação Legal / Segurança | O sistema mascara ativamente PIIs duros antes de qualquer envio ao LLM via Expressões Regulares (Regex). |
| **Prompt do LLM** | CV Anonimizado | Legítimo Interesse (Art. 7º, IX) | Geração de score técnico. |

### 3.3 Política de Retenção e Exclusão
* **Tempo de Retenção:** Currículos em texto são retidos unicamente pelo tempo do ciclo da vaga (estipulado tecnicamente em 6 meses).
* **Mecanismo de Exclusão:** Para garantir a exclusão real (superando a mera intenção), foi implementado um script utilitário (`scripts/limpeza_retencao.py`) que varre a base de dados e deleta fisicamente os arquivos.
* **Backups e Snapshots:** Cópias de segurança do sistema de banco de dados e arquivos herdam rigorosamente a mesma política de retenção do dado principal, sendo destruídas de forma irreversível ao fim do ciclo de 6 meses.

## 4. Segurança e Rotação de Credenciais
O vazamento de chaves é um risco crítico. Nossa política estabelece:
1. **Zero Hardcoding:** Segredos vivem apenas em `.env` local (bloqueado via `.gitignore`) e *Secrets* na infraestrutura em nuvem.
2. **Procedimento de Rotação:** Em caso de vazamento detectado via auditoria (ex: `gitleaks`), a equipe deve: **(1)** Revogar a chave imediatamente no painel do provedor da API; **(2)** Gerar nova chave e injetá-la no ambiente de produção; **(3)** Registrar o incidente em um Post-mortem, sendo proibido tentar encobrir o vazamento reescrevendo o histórico do Git.
3. **Privacidade nos Logs:** É estritamente proibido o registro (log) de dados pessoais em claro. Qualquer necessidade de rastreabilidade de currículos no backend deve utilizar hash criptográfico ou IDs de referência.

## 5. Pontos não-resolvidos (Dívida Técnica Ativa)

> Esta seção lista questões em aberto que precisam ser endereçadas nas próximas fases de evolução do sistema.

- **TODO — Viés de gênero:** definir métricas (disparate impact ratio, equal opportunity difference) e thresholds aceitáveis. Quem audita? Com que frequência?
- **TODO — Viés de idade:** o sistema atual pondera "anos de experiência" — isso correlaciona com idade. Como mitigar sem perder sinal legítimo?
- **TODO — Viés geográfico:** CEP, cidade, estado de formação são proxies fortes para classe social. Política de mascaramento avançada?
- **TODO — Auditabilidade:** formato, retenção e acesso ao log de decisões. Quem pode consultar? Por quanto tempo guardamos?
- **TODO — Direito à revisão:** desenho operacional do fluxo Art. 20. Botão na UI do recrutador? Canal externo para candidato?
- **TODO — Comunicação ao candidato:** o candidato sabe que seu CV está sendo pontuado por IA? Onde isso aparece?
- **TODO — Dados Sensíveis (Indiretos):** A sanitização atual (Regex) mascara e-mails, CPFs e telefones, mas não detecta dados indiretos (origem racial via foto, religião via instituição, condição de saúde). É necessário implementar detecção avançada via NER (ex: Spacy).

✅ **[RESOLVIDO] — Transferência internacional:** O uso da API da Anthropic envolve transferência internacional, porém a base legal e a segurança foram garantidas pela implementação de uma função obrigatória de sanitização (Regex) que bloqueia o envio de PIIs duros nos prompts, mitigando o risco de exposição cruzada de fronteiras.

## 6. Governança

Comitê de Ética em IA — composto por: Diretoria de Plataforma, DPO, Jurídico, Recrutamento, Diversidade & Inclusão, representante externo (acadêmico).

Reuniões trimestrais. Decisões registradas em ata pública interna.

* **DPA (Data Processing Agreement):** A transferência de dados anonimizados para a Anthropic/OpenAI é regida e protegida pelo aceite do DPA padrão do provedor.

* **Encarregado de Dados (DPO):** Bárbara atua como DPO e responsável pelas decisões de privacidade nesta fase da arquitetura.