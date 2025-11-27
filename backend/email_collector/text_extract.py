"""Safe text extraction helpers for PDF and DOCX.

Imports are performed lazily so the package can be imported even if
optional dependencies (PyMuPDF / python-docx) are not installed.
"""

def extract_text_from_pdf(filepath):
    try:
        import fitz
    except Exception:
        raise ImportError("PyMuPDF (fitz) is required to extract text from PDFs. Install 'pymupdf'.")

    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception:
        return ""


def extract_text_from_docx(filepath):
    try:
        import docx
    except Exception:
        raise ImportError("python-docx is required to extract text from DOCX files. Install 'python-docx'.")

    try:
        doc = docx.Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.strip()
    except Exception:
        return ""


def extract_text(filepath):
    path = filepath.lower()
    if path.endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    if path.endswith(".docx"):
        return extract_text_from_docx(filepath)
    return ""
