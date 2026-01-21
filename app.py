import streamlit as st
import random
from docx import Document
from io import BytesIO
from fpdf import FPDF
from pptx import Presentation
import PyPDF2
import re
import unicodedata
import base64

# --- Normalização de texto ---
def normalizar_texto(texto):
    if not texto:
        return ""
    texto = unicodedata.normalize("NFC", texto)
    texto = "".join(ch for ch in texto if unicodedata.category(ch)[0] != "C")
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

# --- Extração de texto ---
def extrair_texto_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texto += t + " "
        return normalizar_texto(texto)
    except:
        return ""

def extrair_texto_word(file):
    try:
        doc = Document(file)
        texto = ""
        for para in doc.paragraphs:
            if para.text.strip():
                texto += para.text + " "
        return normalizar_texto(texto)
    except:
        return ""

def extrair_texto_pptx(file):
    try:
        prs = Presentation(file)
        texto = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape,"text") and shape.text.strip():
                    texto += shape.text + " "
        return normalizar_texto(texto)
    except:
        return ""

# --- Separar sentenças ---
def separar_sentencas(texto):
    partes = re.split(r'(?<=[.!?])\s+', texto)
    return [p.strip() for p in partes if len(p.strip()) > 20]

# --- Gerar alternativas genéricas ---
def gerar_alternativas_gen(texto):
    correta = texto
    incorretas = [
        "Afirmação incorreta relacionada ao tema.",
        "Fato não relacionado ao conteúdo apresentado.",
        "Esta alternativa não corresponde ao texto.",
        "Informação incorreta sobre o assunto."
    ]
    alternativas = [correta] + random.sample(incorretas, 4)
    random.shuffle(alternativas)
    letras = ["A","B","C","D","E"]
    return {letras[i]: alt for i, alt in enumerate(alternativas)}

# --- Gerar questão ---
def gerar_questao(texto):
    sentencas = separar_sentencas(texto)
    if not sentencas:
        contexto = "Texto insuficiente para gerar questão."
    else:
        contexto = random.choice(sentencas)
    enunciado = "Com base no trecho acima, assinale a alternativa correta sobre o que é descrito:"
    alternativas = gerar_alternativas_gen(contexto)
    letra_correta = [l for l,alt in alternativas.items() if alt == contexto][0]
    return {"contexto": contexto,"enunciado": enunciado,"alternativas": alternativas,"correta": letra_correta}

# --- Exportar Word ---
def gerar_word(questoes):
    doc = Document()
    doc.add_heading("Prova Gerada", level=1)
    for i,q in enumerate(questoes,1):
        doc.add_paragraph(f"Questão {i}")
        doc.add_paragraph(q["contexto"])
        doc.add_paragraph(q["enunciado"])
        for letra,alt in q["alternativas"].items():
            doc.add_paragraph(f"{letra}) {alt}")
        doc.add_paragraph(f"Gabarito: {q['correta']}")
        doc.add_paragraph("")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- Exportar PDF ---
def gerar_pdf(questoes):
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i,q in enumerate(questoes,1):
        pdf.multi_cell(0,8,f"Questão {i}")
        pdf.multi_cell(0,8,q["contexto"])
        pdf.multi_cell(0,8,q["enunciado"])
        for letra,alt in q["alternativas"].items():
            pdf.multi_cell(0,8,f"{letra}) {alt}")
        pdf.multi_cell(0,8,f"Gabarito: {q['correta']}")
        pdf.ln(5)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Streamlit ---
st.set_page_config(page_title="Gerador de Questões Grátis", layout="centered")
st.title("Gerador de Questões – Versão Gratuita")
st.write("Cole o texto ou envie PDF, Word ou PowerPoint. Alternativa correta vem do texto; as incorretas são genéricas.")

texto = st.text_area("Cole o texto aqui:", height=200)
uploaded_file = st.file_uploader("Ou envie um arquivo:", type=['pdf','docx','pptx'])
if uploaded_file:
    if uploaded_file.name.lower().endswith('.pdf'):
        texto = extrair_texto_pdf(uploaded_file)
    elif uploaded_file.name.lower().endswith('.docx'):
        texto = extrair_texto_word(uploaded_file)
    elif uploaded_file.name.lower().endswith('.pptx'):
        texto = extrair_texto_pptx(uploaded_file)

quantidade = st.number_input("Quantas questões gerar?", min_value=1, max_value=50, value=5)

if st.button("🧠 Gerar questões"):
    if not texto.strip():
        st.warning("Insira um texto ou envie um arquivo válido.")
    else:
        questoes = [gerar_questao(texto) for _ in range(quantidade)]
        for i,q in enumerate(questoes,1):
            st.subheader(f"Questão {i}")
            st.write(q["contexto"])
            st.markdown(f"**{q['enunciado']}**")
            for letra,alt in q["alternativas"].items():
                st.write(f"{letra}) {alt}")
            st.success(f"✔️ Alternativa correta: {q['correta']}")
            st.divider()

        buf_word = gerar_word(questoes)
        b64w = base64.b64encode(buf_word.read()).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64w}" download="Prova.docx">💾 Baixar Word</a>', unsafe_allow_html=True)

        buf_pdf = gerar_pdf(questoes)
        b64p = base64.b64encode(buf_pdf.read()).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64p}" download="Prova.pdf">💾 Baixar PDF</a>', unsafe_allow_html=True)
