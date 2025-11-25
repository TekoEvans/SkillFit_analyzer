import os
import json
import re
from fetch_emails import fetch_annonce_pdfs
from pdf_extractor import extract_pdf_text
from llm_parser import analyze_offer
from dotenv import load_dotenv

# Charger variables d'environnement
load_dotenv()

# Dossier de sortie pour les JSON
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Fonction pour nettoyer le texte PDF
def clean_pdf_text(text):
    """
    Nettoyage avancé :
    - Supprime les retours à la ligne inutiles
    - Supprime les espaces insérés dans les mots
    - Remplace les multiples espaces par un seul
    - Supprime les caractères invisibles
    """
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'(\w)\s+(\w)', r'\1\2', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

# Fonction pour sauvegarder le JSON
def save_json(content, filename):
    path = os.path.join(OUTPUT_DIR, filename)

    # Nettoyage caractères invisibles / spéciaux
    content_clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', content)

    try:
        data = json.loads(content_clean)
    except json.JSONDecodeError:
        data = {"error": "Invalid JSON returned by LLM", "raw": content_clean}

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    print("=== Agent SkillFit → Analyse des Offres ===")

    pdf_files = fetch_annonce_pdfs()
    if not pdf_files:
        print("Aucun PDF trouvé dans les emails.")
        return

    for email_id, pdf_path in pdf_files:
        print(f"📄 Lecture PDF → {pdf_path}")

        # Extraction + nettoyage du texte
        text = extract_pdf_text(pdf_path)
        text = clean_pdf_text(text)

        # Analyse via LLM
        json_output = analyze_offer(text)

        # 🆕 Utiliser nom du PDF comme nom du JSON
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        out_name = f"{pdf_name}.json"

        save_json(json_output, out_name)

        print(f"✔ JSON généré : {OUTPUT_DIR}/{out_name}")

    print("\n=== Terminé ===")

if __name__ == "__main__":
    main()
