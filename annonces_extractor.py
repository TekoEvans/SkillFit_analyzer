import os
import json
import re
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

# =============================================
# CONFIG
# =============================================
INPUT_DIR = "downloads"
OUTPUT_DIR = "outputs"
PROMPT_FILE = "prompt.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =============================================
# FONCTION : Nettoyage du texte PDF
# =============================================
def clean_pdf_text(text: str) -> str:
    # Supprimer les espaces multiples
    text = re.sub(r"\s+", " ", text)

    # Supprimer les espaces au début/fin
    text = text.strip()

    return text

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

    with open(PROMPT_FILE, "r", encoding="utf8") as f:
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
def run():
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".pdf")]

    if not pdf_files:
        print("❌ Aucun PDF trouvé dans downloads/")
        return

    print(f"📄 {len(pdf_files)} PDF détectés.")

    offre_index = 1

    for pdf_name in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_name)
        print(f"\n➡ Traitement : {pdf_name}")

        # Extraire texte
        text = extract_pdf_text(pdf_path)
        text = clean_pdf_text(text)

        # LLM → JSON brut
        raw_json = analyze_offer(text)

        # Nettoyage JSON
        clean_raw = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_json)

        # Parse ou erreur
        try:
            data = json.loads(clean_raw)
        except:
            data = {"error": "Invalid JSON returned by LLM", "raw": clean_raw}

        # Ajouter metadata
        data["offre_id"] = f"ANN-{offre_index:02d}"
        data["filename"] = pdf_name

        # date de création du PDF
        timestamp = os.path.getmtime(pdf_path)
        data["offre_date"] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

        # Sauvegarde
        out_path = os.path.join(OUTPUT_DIR, f"{pdf_name.replace('.pdf','')}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"✔ JSON généré → {out_path}")

        offre_index += 1

    print("\n=== Terminé ===")

# =============================================
# Lancement
# =============================================
if __name__ == "__main__":
    run()