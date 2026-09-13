# Briefing — TalentoBR | CV Screener

**De:** Renata Almeida, Diretora de Plataforma — TalentoBR
**Para:** AI Engineer Pleno (Plataforma)
**Data:** início deste ano

---

Oi, bem-vinda(o) ao time. Vou te contar onde a gente está, o que precisa acontecer nas próximas 12 semanas e por que esse projeto é, simultaneamente, o de maior impacto comercial e o de maior risco regulatório que temos hoje.

## Quem somos

A TalentoBR é uma HR-tech estabelecida há quase dez anos. Somos 350 funcionários, atendemos cerca de 600 empresas-cliente — de fintechs de 30 pessoas a varejistas com folha de mais de 20 mil. Nossa missão, escrita lá em 2017 e que ninguém deixa ninguém esquecer, é simples: **"o match certo entre vaga e pessoa, sem viés"**. Os dois pedaços dessa frase importam igual.

## Sua função

Você foi contratada(o) como AI Engineer Pleno na Plataforma. Isso significa: você não é a pessoa que faz pesquisa de modelo, e também não é só infra. Você é a ponte entre o que o time de Data prova em notebook e o que vira produto na mão de recrutador — com tudo que isso implica de auth, persistência, log, observabilidade, custo e (principalmente) conformidade.

## Onde estamos

Em dezembro o time de Data entregou um protótipo de triagem de CVs. Hoje é um **notebook Jupyter** que faz parsing de PDF com `pypdf`, joga o texto numa chamada de OpenAI, extrai campos estruturados, compara com a descrição da vaga e devolve um score híbrido (heurística + LLM) de 0 a 100 com uma justificativa em texto livre. Roda. Funciona em laboratório.

**O que não tem:** API. UI. autenticação. multi-tenant. persistência. log de decisão. análise de viés. monitoramento de custo. observabilidade. plano de LGPD. nada.

## Onde precisamos chegar em 12 semanas

1. Sistema **usado de verdade** por recrutadores das nossas empresas-cliente — não um protótipo de demo.
2. URL **multi-tenant**: cliente A não pode em hipótese nenhuma enxergar dados do cliente B.
3. **Log auditável de toda decisão** — quem pediu, qual CV, qual vaga, qual score, qual modelo, qual prompt, qual versão. Imutável, exportável.
4. **Pitch para o Comitê de Ética em IA** da TalentoBR. Eles vão querer ver mapa de viés, plano de mitigação e como o sistema respeita o **Art. 20 da LGPD** (direito à revisão humana de decisão automatizada).

## Restrições inegociáveis

- **Custo:** US$ 250/mês para processar 10 mil currículos/mês. Acima disso, alarme vermelho.
- **LGPD — categoria especial:** dados de saúde, **não** processar nunca. Mas atenção: **formação e origem geográfica podem virar proxies sensíveis** para raça e classe. Trate como se fossem.
- **ANPD:** fiscalizou três concorrentes nossas no ano passado. Vão olhar pra gente cedo ou tarde.
- **Art. 20 LGPD:** toda decisão suportada por IA tem que ter caminho claro de **revisão humana**. Recrutador é quem decide; o sistema **apoia**.

## O que eu espero de você

Que pergunte o tempo todo "isso é justo?" antes de "isso é rápido?". Que documente. Que pense em quem está do outro lado — a pessoa cujo currículo está sendo pontuado por uma máquina. E que, no final das 12 semanas, eu consiga olhar pro Comitê de Ética e dizer: "olha, fizemos certo".

Boa jornada.

— Renata
