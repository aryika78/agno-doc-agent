from docx import Document
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\MYWORK\At AI_ML_Int\Agno\poppler\poppler-25.12.0\Library\bin"


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])


def load_pdf(path: str) -> str:
    # Try normal text extraction first
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"

    # If text extraction got nothing, fall back to OCR
    if not text.strip():
        images = convert_from_path(path, poppler_path=POPPLER_PATH)
        text = "\n".join(pytesseract.image_to_string(img) for img in images)

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
