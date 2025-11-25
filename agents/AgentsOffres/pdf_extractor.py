import PyPDF2

def extract_pdf_text(filepath):
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text
