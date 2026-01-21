import streamlit as st
import random
from docx import Document
from io import BytesIO
import base64
from fpdf import FPDF
import PyPDF2
from docx import Document as DocxDocument
from pptx import Presentation

# Função para extrair texto de PDF
def extrair_texto_pdf(file):
    reader = PyPDF2.PdfReader(file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    return texto

# Função para extrair texto de Word
def extrair_texto_word(file):
    doc = DocxDocument(file)
    texto = ""
    for para in doc.paragraphs:
        texto += para.text + "\n"
    return texto

# Função para extrair texto de PowerPoint
def extrair_texto_pptx(file):
    prs = Presentation(file)
    texto = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                texto += shape.text + "\n"
    return texto

# Função para gerar questão ENEM
def gerar_questao_enem(texto_base):
    if len(texto_base.strip()) < 50:
        texto_base += " (adicionando texto de exemplo para preencher contexto.)"
    contexto = f"Considere o texto a seguir:\n\n{texto_base[:300]}..."
    enunciado = "A partir das informações apresentadas no texto, assinale a alternativa que melhor interpreta a situação apresentada."
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

# Função para gerar Word
def gerar_word(questoes):
    doc = Document()
    for i, q in enumerate(questoes, 1):
        doc.add_paragraph(f"Questão {i}")
        doc.add_paragraph(q["contexto"])
        doc.add_paragraph(q["enunciado"])
        for alt in q["alternativas"]:
            doc.add_paragraph(f"- {alt}")
        doc.add_paragraph(f"Resposta correta: {q['correta']}")
        doc.add_paragraph("\n")
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Função para gerar PDF
def gerar_pdf(questoes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i, q in enumerate(questoes, 1):
        pdf.multi_cell(0, 8, f"Questão {i}")
        pdf.multi_cell(0, 8, q["contexto"])
        pdf.multi_cell(0, 8, q["enunciado"])
        for alt in q["alternativas"]:
            pdf.multi_cell(0, 8, f"- {alt}")
        pdf.multi_cell(0, 8, f"Resposta correta: {q['correta']}")
        pdf.ln(5)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- STREAMLIT INTERFACE ---
st.title("Gerador de Questões ENEM - Word e PDF")
st.write("Cole o texto ou envie um arquivo PDF, Word ou PowerPoint para gerar questões automaticamente.")

# Input de texto
texto = st.text_area("Digite ou cole o texto aqui (até 3000 caracteres):", "", height=150)

# Upload de arquivos
uploaded_file = st.file_uploader("Ou envie um arquivo:", type=['pdf','docx','pptx'])
if uploaded_file is not None:
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
    if texto.strip() == "":
        st.warning("⚠️ Insira um texto ou envie um arquivo para gerar as questões.")
    else:
        questoes_geradas = []
        for i in range(quantidade):
            questao = gerar_questao_enem(texto)
            questoes_geradas.append(questao)

            st.subheader(f"📝 Questão {i+1} – Modelo ENEM")
            st.text(questao["contexto"])
            st.markdown(f"**{questao['enunciado']}**")
            for alt in questao["alternativas"]:
                st.write(f"- {alt}")
            st.success(f"✔️ Resposta correta: {questao['correta']}")
            st.divider()

        # Botão para exportar Word
        buffer_word = gerar_word(questoes_geradas)
        b64_word = base64.b64encode(buffer_word.read()).decode()
        href_word = f'<a href="data:application/octet-stream;base64,{b64_word}" download="Prova_ENEM.docx">💾 Baixar Prova em Word</a>'
        st.markdown(href_word, unsafe_allow_html=True)

        # Botão para exportar PDF
        buffer_pdf = gerar_pdf(questoes_geradas)
        b64_pdf = base64.b64encode(buffer_pdf.read()).decode()
        href_pdf = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="Prova_ENEM.pdf">💾 Baixar Prova em PDF</a>'
        st.markdown(href_pdf, unsafe_allow_html=True)
