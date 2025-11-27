import os
import json
import re
from pathlib import Path
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

# =============================================
# CONFIG
# =============================================

OUTPUT_DIR = "outputs"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROMPT_PATH = os.path.join(Path(__file__).resolve().parent, "prompt.txt")
os.makedirs(OUTPUT_DIR, exist_ok=True)



# pdf_path = os.path.join(PDF_UPLOAD_DIR, uploaded_pdf.name)


# =============================================
# FONCTION : Nettoyage du texte PDF
# =============================================
def clean_pdf_text(text):
    # Fusion des mots coupés ("V ous" → "Vous")
    text = re.sub(r"(\w)\s+(\w)", r"\1\2", text)

    # Remplacer les multiples espaces
    text = re.sub(r"\s+", " ", text)

    # Retirer caractères invisibles
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)

    return text.strip()

# =============================================
# FONCTION : extraction texte PDF
# =============================================
def extract_pdf_text(path):
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise Exception("Installe PyPDF2 → pip install PyPDF2")

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"

    return text

# =============================================
# FONCTION : appel LLM Groq
# =============================================
def analyze_offer(text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    with open(PROMPT_PATH, "r", encoding="utf8") as f:
        base_prompt = f.read()

    res = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": text}
        ]
    )

    return res.choices[0].message.content

# =============================================
# MAIN LOGIQUE : parcours PDFs
# =============================================



def run(pdf_name):
    # pdf path
    pdf_path =  Path(BASE_DIR)/"offres_pdf"/pdf_name
    # Nom du fichier à partir du chemin
    # pdf_name = os.path.basename(pdf_path)

    print(f"\n➡ Traitement : {pdf_name}")

    # Extraire texte PDF
    text = extract_pdf_text(pdf_path)
    text = clean_pdf_text(text)

    # LLM → JSON brut
    raw_json = analyze_offer(text)

    # Nettoyage caractères invisibles
    clean_raw = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_json)

    # Parsing JSON
    try:
        data = json.loads(clean_raw)
    except:
        data = {"error": "Invalid JSON returned by LLM", "raw": clean_raw}

    # Ajouter metadata
    data["filename"] = pdf_name

    # Date du PDF
    timestamp = os.path.getmtime(pdf_path)
    data["offer_date"] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    # Sauvegarde
    out_path = os.path.join(OUTPUT_DIR, f"{pdf_name.replace('.pdf','')}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✔ JSON généré → {out_path}")

    # Retourner uniquement le JSON
    return data

# =============================================
# Lancement
# =============================================
if __name__ == "__main__":
    print(run("annonce_data.pdf"))
    
    
    
