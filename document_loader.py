from docx import Document
from PyPDF2 import PdfReader


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def load_document(path: str) -> str:
    if path.endswith(".txt"):
        return load_txt(path)
    elif path.endswith(".docx"):
        return load_docx(path)
    elif path.endswith(".pdf"):
        return load_pdf(path)
    else:
        raise ValueError("Unsupported file format")
