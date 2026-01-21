import streamlit as st
import random

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

# Campo de texto para input
st.subheader("📄 Inserir conteúdo")
texto = st.text_area(
    "Cole aqui o texto base para gerar as questões:",
    height=200
)

# Configurações
st.subheader("⚙️ Configurações")
quantidade = st.slider(
    "Quantidade de questões",
    min_value=1,
    max_value=20,
    value=5
)

modelo = st.selectbox(
    "Modelo de avaliação",
    ["Geral", "ENEM", "ENADE", "Concurso"]
)

st.divider()

# Função para parâmetros do modelo
def parametros_modelo(modelo):
    if modelo == "ENEM":
        return {
            "tipo": "Múltipla escolha",
            "alternativas": 5,
            "estilo": "contextualizada",
            "nivel": "interpretação e aplicação",
            "linguagem": "competências e habilidades"
        }
    else:
        return {
            "tipo": "Múltipla escolha",
            "alternativas": 4,
            "estilo": "direta",
            "nivel": "conteudista",
            "linguagem": "objetiva"
        }

# Função para gerar questão ENEM
def gerar_questao_enem(texto_base):
    # Garantir que sempre haja texto suficiente
    if len(texto_base.strip()) < 50:
        texto_base += " (adicionando texto de exemplo para preencher contexto.)"

    contexto = f"Considere o texto a seguir:\n\n{texto_base[:300]}..."
    
    enunciado = (
        "A partir das informações apresentadas no texto, "
        "assinale a alternativa que melhor interpreta a situação apresentada."
    )
    
    alternativas = [
        "A alternativa correta está associada à interpretação contextual do texto.",
        "A alternativa apresenta uma conclusão parcial e limitada.",
        "A alternativa generaliza informações sem considerar o contexto.",
        "A alternativa desconsidera elementos centrais do texto.",
        "A alternativa interpreta corretamente a relação entre os elementos apresentados."
    ]
    
    correta = alternativas[-1]
    random.shuffle(alternativas)

    return {
        "contexto": contexto,
        "enunciado": enunciado,
        "alternativas": alternativas,
        "correta": correta
    }

# Botão para gerar questões
if st.button("🧠 Gerar questões"):
    if texto.strip() == "":
        st.warning("⚠️ Insira um texto para gerar as questões.")
    else:
        params = parametros_modelo(modelo)

        if modelo == "ENEM":
            # Gerar a quantidade de questões selecionada
            for i in range(quantidade):
                questao = gerar_questao_enem(texto)
                
                st.subheader(f"📝 Questão {i+1} – Modelo ENEM")
                st.text(questao["contexto"])
                st.markdown(f"**{questao['enunciado']}**")
                
                for alt in questao["alternativas"]:
                    st.write(f"- {alt}")
                
                st.success(f"✔️ Resposta correta (gabarito): {questao['correta']}")
                st.divider()
        else:
            st.info("Outros modelos serão implementados em breve.")
