import streamlit as st
import random
from docx import Document
from io import BytesIO
from fpdf import FPDF
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation
import re
import base64

# --- Funções utilitárias ---
def limpar_texto(texto):
    """Remove caracteres inválidos e espaços extras, mantendo frases completas."""
    if texto is None:
        return ""
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\x00-\x7F]+','', texto)
    return texto.strip()

def extrair_texto_pdf(file):
    reader = PyPDF2.PdfReader(file)
    texto = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texto += page_text + " "
    return limpar_texto(texto)

def extrair_texto_word(file):
    doc = DocxDocument(file)
    texto = ""
    for para in doc.paragraphs:
        if para.text.strip():
            texto += para.text + " "
    return limpar_texto(texto)

def extrair_texto_pptx(file):
    prs = Presentation(file)
    texto = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                texto += shape.text + " "
    return limpar_texto(texto)

# --- Função para gerar questões com alternativas inventadas ---
def gerar_questao(texto_base):
    frases = [f.strip() for f in texto_base.split('.') if len(f.strip()) > 40]
    if not frases:
        frases = ["Texto insuficiente para gerar questão."]
    
    contexto = random.choice(frases)
    
    # Enunciado baseado em palavras do contexto
    palavras = contexto.split()
    chave = " ".join(random.sample(palavras, min(3, len(palavras)))) if len(palavras) > 5 else "interpretação do texto"
    enunciado = f"Com base no texto acima, assinale a alternativa que melhor se refere à {chave}."

    # Alternativa correta
    correta = contexto

    # Alternativas incorretas totalmente inventadas
    incorretas = [
        "Informação incorreta sobre o assunto.",
        "Esta alternativa não corresponde ao texto.",
        "Fato não relacionado ao conteúdo apresentado.",
        "Afirmação falsa para confundir o leitor."
    ]
    alternativas = [correta] + incorretas
    random.shuffle(alternativas)

    return {
        "contexto": contexto,
        "enunciado": enunciado,
        "alternativas": alternativas,
        "correta": correta
    }

# --- Funções de exportação ---
def gerar_word(questoes):
    doc = Document()
    for i, q in enumerate(questoes, 1):
        doc.add_paragraph(f"Questão {i}")
        doc.add_paragraph(q.get("contexto",""))
        doc.add_paragraph(q.get("enunciado",""))
        for alt in q.get("alternativas", []):
            doc.add_paragraph(f"- {alt}")
        doc.add_paragraph(f"Resposta correta: {q.get('correta','')}")
        doc.add_paragraph("\n")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def gerar_pdf(questoes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i, q in enumerate(questoes, 1):
        pdf.multi_cell(0, 8, f"Questão {i}")
        pdf.multi_cell(0, 8, q.get("contexto",""))
        pdf.multi_cell(0, 8, q.get("enunciado",""))
        for alt in q.get("alternativas", []):
            pdf.multi_cell(0, 8, f"- {alt}")
        pdf.multi_cell(0, 8, f"Resposta correta: {q.get('correta','')}")
        pdf.ln(5)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- STREAMLIT INTERFACE ---
st.title("Gerador de Questões – Versão Gratuita com Alternativas Inventadas")
st.write("Cole o texto ou envie um arquivo PDF, Word ou PowerPoint para gerar questões automaticamente.")

# Input de texto
texto = st.text_area("Digite ou cole o texto aqui:", "", height=150)

# Upload de arquivo
uploaded_file = st.file_uploader("Ou envie um arquivo:", type=['pdf','docx','pptx'])
if uploaded_file:
    if uploaded_file.name.endswith('.pdf'):
        texto = extrair_texto_pdf(uploaded_file)
    elif uploaded_file.name.endswith('.docx'):
        texto = extrair_texto_word(uploaded_file)
    elif uploaded_file.name.endswith('.pptx'):
        texto = extrair_texto_pptx(uploaded_file)

# Quantidade de questões
quantidade = st.number_input("Quantas questões deseja gerar?", min_value=1, max_value=50, value=5)

# Botão para gerar questões
if st.button("🧠 Gerar questões"):
    if not texto.strip():
        st.warning("⚠️ Insira um texto ou envie um arquivo para gerar as questões.")
    else:
        questoes_geradas = []
        for i in range(quantidade):
            questao = gerar_questao(texto)
            questoes_geradas.append(questao)

            st.subheader(f"📝 Questão {i+1}")
            st.text(questao["contexto"])
            st.markdown(f"**{questao['enunciado']}**")
            for alt in questao["alternativas"]:
                st.write(f"- {alt}")
            st.success(f"✔️ Resposta correta: {questao['correta']}")
            st.divider()

        # Exportar Word
        buffer_word = gerar_word(questoes_geradas)
        b64_word = base64.b64encode(buffer_word.read()).decode()
        href_word = f'<a href="data:application/octet-stream;base64,{b64_word}" download="Prova.docx">💾 Baixar Prova em Word</a>'
        st.markdown(href_word, unsafe_allow_html=True)

        # Exportar PDF
        buffer_pdf = gerar_pdf(questoes_geradas)
        b64_pdf = base64.b64encode(buffer_pdf.read()).decode()
        href_pdf = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Prova.pdf">💾 Baixar Prova em PDF</a>'
        st.markdown(href_pdf, unsafe_allow_html=True)
