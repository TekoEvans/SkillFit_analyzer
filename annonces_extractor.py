import os
import json
import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# Charger variables d'environnement
load_dotenv()

PROMPT_FILE = "prompt.txt"


# ======================================================
# Nettoyage texte PDF
# ======================================================
def clean_pdf_text(text):
    text = re.sub(r"(\w)\s+(\w)", r"\1\2", text)      # Répare "V ous" → "Vous"
    text = re.sub(r"\s+", " ", text)                 # Multiples espaces → 1
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text) # Caractères invisibles
    return text.strip()


# ======================================================
# Extraction texte PDF
# ======================================================
def extract_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"

    return text


# ======================================================
# Appel LLM Groq
# ======================================================
def analyze_offer(text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    with open(PROMPT_FILE, "r", encoding="utf8") as f:
        base_prompt = f.read()

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": text}
        ]
    )

    return response.choices[0].message.content


# ======================================================
# Fonction principale : traite 1 PDF → retourne JSON
# ======================================================
def process_pdf(pdf_path: str, offre_index: int = 1):
    pdf_name = os.path.basename(pdf_path)

    # 1. Extraire et nettoyer texte
    raw_text = extract_pdf_text(pdf_path)
    clean_text = clean_pdf_text(raw_text)

    # 2. LLM → JSON brut (string)
    raw_json = analyze_offer(clean_text)

    # 3. Nettoyer pour éviter erreurs JSON
    clean_raw = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_json)

    # 4. Convertir en dict Python
    try:
        data = json.loads(clean_raw)
    except:
        data = {"error": "Invalid JSON returned by LLM", "raw": clean_raw}

    # 5. Ajouter metadata
    data["offre_id"] = f"ANN-{offre_index:02d}"
    data["filename"] = pdf_name
    data["offre_date"] = datetime.fromtimestamp(os.path.getmtime(pdf_path)).strftime("%Y-%m-%d")

    return data

# Test de l'extraction à supprimer 
if __name__ == "__main__":
    result = process_pdf("downloads/annonce_data.pdf", offre_index=1)
    print(json.dumps(result, indent=4, ensure_ascii=False))
