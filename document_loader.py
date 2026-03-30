import os
from dotenv import load_dotenv
from docx import Document
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path

load_dotenv()

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")
POPPLER_PATH = os.getenv("POPPLER_PATH", None)


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
        try:
            images = convert_from_path(path, poppler_path=POPPLER_PATH)
            text = "\n".join(pytesseract.image_to_string(img) for img in images)
        except Exception as e:
            raise ValueError(
                f"This PDF appears to be scanned/image-based but OCR failed: {e}. "
                "Ensure Tesseract and Poppler are installed."
            )

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
