import streamlit as st

st.set_page_config(
    page_title="Gerador de Questões Educacionais",
    page_icon="📘",
    layout="centered"
)

st.title("📘 Gerador de Questões Educacionais")
st.markdown(
    "Aplicativo para professores gerarem questões automaticamente a partir de textos."
)

st.divider()

st.subheader("📄 Inserir conteúdo")

texto = st.text_area(
    "Cole aqui o texto base para gerar as questões:",
    height=200
)

st.subheader("⚙️ Configurações")

quantidade = st.slider(
    "Quantidade de questões",
    min_value=1,
    max_value=20,
    value=5
)

tipo = st.selectbox(
    "Tipo de questão",
    ["Múltipla escolha", "Verdadeiro ou Falso", "Discursiva"]
)

modelo = st.selectbox(
    "Modelo de avaliação",
    ["Geral", "ENEM", "ENADE", "Concurso"]
)

st.divider()

if st.button("🧠 Gerar questões"):
    if texto.strip() == "":
        st.warning("⚠️ Insira um texto para gerar as questões.")
    else:
        st.success("✅ Texto recebido! Em breve as questões aparecerão aqui.")
