# Segurança, Conformidade e LGPD

Este documento centraliza as políticas de governança de dados e segurança da aplicação **TalentoBR**, alinhando o projeto às exigências da LGPD e às melhores práticas de DevSecOps.

## 1. Mapa de Dados e Base Legal (Art. 7º LGPD)

| Ponto de Coleta | Dados Pessoais | Base Legal (LGPD) | Justificativa |
| :--- | :--- | :--- | :--- |
| **Upload de Currículo** | Trajetória, formação, competências | Execução de Contrato (Art. 7º, V) | Necessário para avaliar o candidato para a vaga aplicada. |
| **Sanitização (Regex)** | E-mail, Telefone, CPF, Links | Obrigação Legal / Segurança | Mascaramento de PII duros antes do processamento externo. |
| **Prompt para o LLM** | Texto do CV anonimizado (sem PII) | Legítimo Interesse (Art. 7º, IX) | O TalentoBR (Controlador) utiliza a Anthropic/OpenAI (Operador) para gerar o score técnico. |

* **Aviso de Transferência Internacional (Art. 33):** Como provedores de LLM processam dados em servidores no exterior (EUA), garantimos a mitigação desse risco sanitizando (mascarando) os PIIs do candidato *antes* da requisição de rede. Nomes ou fragmentos que escapem à sanitização inicial estão acobertados pelas cláusulas-padrão contratuais (DPA) do provedor.

## 2. Política de Retenção e Exclusão

* **Tempo de Retenção:** Currículos em texto (e resultados de avaliação) são retidos ativamente apenas pelo tempo de fechamento da vaga (estipulado tecnicamente em 6 meses).
* **Mecanismo de Exclusão:** Para garantir a exclusão real (superando a mera intenção), foi implementado um script utilitário (`scripts/limpeza_retencao.py`) que varre a base de dados (ou diretório de arquivos) e deleta fisicamente registros mais antigos que o limite de retenção.

## 3. Rotação de Credenciais e Gestão de Segredos

O vazamento de chaves é um risco crítico. Nossa política estabelece:
1. **Zero Hardcoding:** Segredos vivem apenas em `.env` local e *Secrets* do Render/GitHub Actions. O arquivo `.env` é bloqueado pelo `.gitignore`.
2. **Procedimento de Rotação (Simulado/Real):** 
   - Caso o `gitleaks` detecte ou haja suspeita de vazamento, o desenvolvedor está proibido de tentar apenas apagar o *commit*.
   - **Passo A:** Acessar imediatamente o painel do provedor (ex: console.anthropic.com) e **revogar/deletar** a chave comprometida.
   - **Passo B:** Gerar uma nova chave e injetá-la no painel de *Environment Variables* do Render.
   - **Passo C:** Registrar o incidente na documentação interna.