"""
UI do recrutador — TalentoBR CV Screener (Streamlit).

Roda com:  streamlit run ui.py
Precisa da API no ar (em outro terminal):  uvicorn app:app --reload

Essa tela é proposital: o recrutador faz upload/cola um CV, cola a vaga, vê o
score e a justificativa. O botão de decisão ("Concordo" / "Discordo") existe pra
reforçar que QUEM DECIDE É A PESSOA (LGPD Art. 20) — mas hoje ele NÃO persiste
nada. É só visual. Persistir essa decisão num log auditável é tarefa do desafio.

Dívida herdada visível aqui:
- URL da API hardcoded.
- Sem login. Sem noção de tenant.
- A decisão do recrutador não é gravada em lugar nenhum.
"""

import io

import requests
import streamlit as st

API_URL = "http://localhost:8000"  # TODO: virar env var, hoje tá cravado


def _ler_upload(arquivo) -> str:
    """Lê texto de um upload .txt ou .pdf."""
    if arquivo.name.lower().endswith(".pdf"):
        import pypdf

        reader = pypdf.PdfReader(io.BytesIO(arquivo.read()))
        return "\n".join((pg.extract_text() or "") for pg in reader.pages)
    return arquivo.read().decode("utf-8", errors="ignore")


def main():
    st.set_page_config(page_title="TalentoBR — Triagem de CVs", page_icon="📄")
    st.title("📄 TalentoBR — Triagem de Currículos")
    st.caption(
        "Ferramenta de APOIO à triagem. O score é um insumo — a decisão é sua "
        "(LGPD Art. 20). Dados de exemplo são sintéticos."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1) Currículo")
        arquivo = st.file_uploader("Upload do CV (.txt ou .pdf)", type=["txt", "pdf"])
        cv_texto = st.text_area(
            "...ou cole o texto do CV aqui",
            height=240,
            placeholder="Cole o conteúdo do currículo",
        )
        if arquivo is not None:
            cv_texto = _ler_upload(arquivo)
            st.info(f"Arquivo lido: {arquivo.name} ({len(cv_texto)} caracteres)")

    with col2:
        st.subheader("2) Vaga")
        titulo = st.text_input("Título da vaga", value="AI Engineer Pleno")
        skills_raw = st.text_input(
            "Skills obrigatórias (separadas por vírgula)",
            value="Python, FastAPI, Docker, LLM, PostgreSQL",
        )
        descricao = st.text_area("Descrição da vaga", height=160)

    if st.button("Pontuar candidato", type="primary"):
        if not cv_texto or not cv_texto.strip():
            st.error("Forneça um CV (upload ou texto).")
            return

        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
        payload = {
            "cv_texto": cv_texto,
            "vaga": {"titulo": titulo, "descricao": descricao, "skills_obrigatorias": skills},
        }

        with st.spinner("Pontuando... (chama a API, que chama o LLM)"):
            try:
                r = requests.post(f"{API_URL}/score", json=payload, timeout=60)
                r.raise_for_status()
            except requests.RequestException as e:
                st.error(f"Falha ao chamar a API ({API_URL}). Ela está no ar? Erro: {e}")
                return

        data = r.json()
        st.session_state["ultimo_resultado"] = data

    # Exibição do resultado (fica fora do if pra sobreviver ao clique do botão de decisão)
    data = st.session_state.get("ultimo_resultado")
    if data:
        st.markdown("---")
        st.metric("Score final (0-100)", data["score_final"])
        c1, c2 = st.columns(2)
        c1.metric("Heurística (skills)", data["score_heuristico"])
        c2.metric("Julgamento LLM", data["score_llm"])
        st.markdown(f"**Justificativa (gerada por IA, post-hoc):** {data['justificativa']}")
        st.caption(f"Modelo: {data.get('modelo', '?')}")
        st.warning(data.get("aviso", ""))

        st.markdown("**Sua decisão (você decide, não a IA):**")
        d1, d2 = st.columns(2)
        # TODO: estes botões NÃO gravam nada. Precisa virar log auditável (Art. 20).
        if d1.button("✅ Concordo / avançar candidato"):
            st.success("Decisão registrada na tela (mas NÃO persistida — ver dívida técnica).")
        if d2.button("❌ Discordo do score"):
            st.info("Discordância registrada na tela (NÃO persistida — ver dívida técnica).")


if __name__ == "__main__":
    main()
