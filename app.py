import streamlit as st
import random
from docx import Document
from io import BytesIO
from fpdf import FPDF
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
import re
import unicodedata
import base64

# --- Funções de normalização ---
def remover_controle(texto):
    return "".join(ch for ch in texto if unicodedata.category(ch)[0] != "C")

def normalizar_texto(texto):
    if texto is None:
        return ""
    texto = unicodedata.normalize("NFC", texto)
    texto = remover_controle(texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()

# --- Extração de texto ---
def extrair_texto_pdf(file):
    try:
        reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + " "
        return normalizar_texto(texto)
    except:
        return ""

def extrair_texto_word(file):
    try:
        doc = DocxDocument(file)
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
                if hasattr(shape, "text") and shape.text.strip():
                    texto += shape.text + " "
        return normalizar_texto(texto)
    except:
        return ""

# --- Separação de sentenças ---
def separar_sentencas(texto):
    if not texto:
        return []
    partes = re.split(r'(?<=[.!?])\s+', texto)
    return [p.strip() for p in partes if len(p.strip()) >= 25]

# --- Gerar alternativas A–E plausíveis ---
def gerar_alternativas(sentenca):
    correta = sentenca
    incorretas = []

    # Substituições sutis para gerar erros plausíveis
    substituicoes = {
        "venoso":"arterial",
        "arterial":"venoso",
        "direito":"esquerdo",
        "esquerdo":"direito",
        "mistura":"não mistura",
        "não mistura":"mistura",
        "diástole":"sístole",
        "sístole":"diástole",
        "contração":"relaxamento",
        "relaxamento":"contração",
        "tecidos":"órgãos"
    }

    for k,v in substituicoes.items():
        if k.lower() in sentenca.lower():
            inc = re.sub(k, v, sentenca, flags=re.IGNORECASE)
            if inc.lower() != correta.lower():
                incorretas.append(inc)

    # Completar 4 alternativas incorretas plausíveis se faltar
    while len(incorretas) < 4:
        incorretas.append("Afirmação incorreta relacionada ao tema.")

    # Seleciona 4 incorretas aleatórias e embaralha com a correta
    alternativas = [correta] + random.sample(incorretas,4)
    random.shuffle(alternativas)

    # Colocar letras A–E
    letras = ["A","B","C","D","E"]
    alternativas_com_letras = {letras[i]: alt for i,alt in enumerate(alternativas)}
    return alternativas_com_letras

# --- Gerar questão ---
def gerar_questao(texto):
    sentencas = separar_sentencas(texto)
    if not sentencas:
        contexto = "Texto insuficiente para gerar questão."
    else:
        contexto = random.choice(sentencas)
    enunciado = "Com base no trecho acima, assinale a alternativa correta sobre o que é descrito:"
    alternativas = gerar_alternativas(contexto)
    # Encontrar letra correta
    letra_correta = [l for l,alt in alternativas.items() if alt==contexto][0]
    return {"contexto": contexto,"enunciado": enunciado,"alternativas": alternativas,"correta": letra_correta}

# --- Exportadores ---
def gerar_word(questoes):
    doc = Document()
    doc.add_heading("Prova Gerada",level=1)
    for i,q in enumerate(questoes,1):
        doc.add_paragraph(f"Questão {i}")
        doc.add_paragraph(q.get("contexto",""))
        doc.add_paragraph(q.get("enunciado",""))
        for letra,alt in q.get("alternativas",{}).items():
            doc.add_paragraph(f"{letra}) {alt}")
        doc.add_paragraph(f"Gabarito: {q.get('correta','')}")
        doc.add_paragraph("")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def gerar_pdf(questoes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i,q in enumerate(questoes,1):
        pdf.multi_cell(0,8,f"Questão {i}")
        pdf.multi_cell(0,8,q.get("contexto",""))
        pdf.multi_cell(0,8,q.get("enunciado",""))
        for letra,alt in q.get("alternativas",{}).items():
            pdf.multi_cell(0,8,f"{letra}) {alt}")
        pdf.multi_cell(0,8,f"Gabarito: {q.get('correta','')}")
        pdf.ln(5)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Streamlit ---
st.set_page_config(page_title="Gerador de Questões Inteligentes", layout="centered")
st.title("Gerador de Questões – Alternativas Inteligentes")
st.write("Cole o texto ou envie PDF, Word ou PowerPoint. Alternativa correta vem do texto; incorretas são pegadinhas plausíveis.")

texto = st.text_area("Cole o texto aqui:",height=200)
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
        questoes = []
        for i in range(quantidade):
            q = gerar_questao(texto)
            questoes.append(q)
            st.subheader(f"Questão {i+1}")
            st.write(q["contexto"])
            st.markdown(f"**{q['enunciado']}**")
            for letra,alt in q["alternativas"].items():
                st.write(f"{letra}) {alt}")
            st.success("✔️ Alternativa correta:")
            st.write(q["correta"])
            st.divider()

        # Downloads
        buf_word = gerar_word(questoes)
        b64w = base64.b64encode(buf_word.read()).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64w}" download="Prova.docx">💾 Baixar Word</a>', unsafe_allow_html=True)

        buf_pdf = gerar_pdf(questoes)
        b64p = base64.b64encode(buf_pdf.read()).decode()
        st.markdown(f'<a href="data:application/octet-stream;base64,{b64p}" download="Prova.pdf">💾 Baixar PDF</a>', unsafe_allow_html=True)
