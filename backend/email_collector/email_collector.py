import os
import json
import base64
import fitz
import docx
import re
from dotenv import load_dotenv
from groq import Groq
from email.utils import parseaddr
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import OrderedDict


# ---------------------------------------------------
# ENV & API
# ---------------------------------------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Dossiers principaux d'organisation
MAIN_CANDIDATES_FOLDER = "candidates"
MAIN_CV_FOLDER = "cv_files"

# Créer les dossiers principaux s'ils n'existent pas
os.makedirs(MAIN_CANDIDATES_FOLDER, exist_ok=True)
os.makedirs(MAIN_CV_FOLDER, exist_ok=True)


# ---------------------------------------------------
# Gmail Service
# ---------------------------------------------------
def get_gmail_service():
    """Authentifie et retourne le service Gmail API"""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------
# Création des dossiers et noms de fichiers dynamiques
# ---------------------------------------------------
def create_output_paths(job_title):
    """
    Crée les chemins de sortie en fonction du poste et de la date
    
    Args:
        job_title: Le poste (ex: "Statisticien")
    
    Returns:
        tuple: (dossier_cv, fichier_json)
    """
    # Normaliser le nom du poste pour le système de fichiers
    safe_job_title = normalize_job_title(job_title)
    safe_job_title = re.sub(r'[^\w\s-]', '', safe_job_title)  # Enlever caractères spéciaux
    safe_job_title = re.sub(r'[-\s]+', '_', safe_job_title)  # Remplacer espaces/tirets par _
    
    # Date du traitement
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Créer les noms avec la date
    cv_folder_name = f"cv_files_{safe_job_title}_{date_str}"
    json_file_name = f"candidates_{safe_job_title}_{date_str}.json"
    
    # Créer les chemins complets dans les dossiers principaux
    cv_folder = os.path.join(MAIN_CV_FOLDER, cv_folder_name)
    json_file = os.path.join(MAIN_CANDIDATES_FOLDER, json_file_name)
    
    # Créer le sous-dossier CV s'il n'existe pas
    os.makedirs(cv_folder, exist_ok=True)
    
    print(f"📂 Structure créée :")
    print(f"   └─ {MAIN_CV_FOLDER}/")
    print(f"      └─ {cv_folder_name}/")
    print(f"   └─ {MAIN_CANDIDATES_FOLDER}/")
    print(f"      └─ {json_file_name}")
    print()
    
    return cv_folder, json_file


# ---------------------------------------------------
# Extraction du poste depuis l'objet de l'email
# ---------------------------------------------------
def extract_job_title_from_subject(subject):
    """
    Extrait le poste depuis l'objet de l'email.
    Format attendu : "Candidature — Poste — Nom Candidat"
    Retourne le poste ou None si non trouvé
    """
    # Patterns possibles pour différents formats
    patterns = [
        r'Candidature\s*[—-]\s*([^—-]+)\s*[—-]',  # Format standard
        r'[—-]\s*([^—-]+)\s*[—-]',  # Juste entre tirets
    ]
    
    for pattern in patterns:
        match = re.search(pattern, subject, re.IGNORECASE)
        if match:
            job_title = match.group(1).strip()
            return job_title
    
    return None


def normalize_job_title(job_title):
    """
    Normalise un titre de poste pour la comparaison
    (enlève accents, espaces multiples, met en minuscules)
    """
    if not job_title:
        return ""
    
    # Remplacer les accents
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c'
    }
    
    job_title = job_title.lower()
    for accent, replacement in replacements.items():
        job_title = job_title.replace(accent, replacement)
    
    # Enlever espaces multiples et trimmer
    job_title = re.sub(r'\s+', ' ', job_title).strip()
    
    return job_title


def job_titles_match(subject_job, target_job):
    """
    Compare deux titres de postes de manière flexible
    """
    normalized_subject = normalize_job_title(subject_job)
    normalized_target = normalize_job_title(target_job)
    
    # Comparaison exacte
    if normalized_subject == normalized_target:
        return True
    
    # Vérifier si l'un contient l'autre
    if normalized_target in normalized_subject or normalized_subject in normalized_target:
        return True
    
    return False


# ---------------------------------------------------
# Extraction texte CV
# ---------------------------------------------------
def extract_text_from_pdf(filepath):
    """Extrait le texte d'un fichier PDF"""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"❌ Erreur extraction PDF {filepath}: {e}")
        return ""


def extract_text_from_docx(filepath):
    """Extrait le texte d'un fichier DOCX"""
    try:
        doc = docx.Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.strip()
    except Exception as e:
        print(f"❌ Erreur extraction DOCX {filepath}: {e}")
        return ""


def extract_text(filepath):
    """Extrait le texte selon l'extension du fichier"""
    if filepath.lower().endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif filepath.lower().endswith(".docx"):
        return extract_text_from_docx(filepath)
    return ""


# ---------------------------------------------------
# Charger prompt
# ---------------------------------------------------
def load_prompt(prompt_file="prompts/prompt.txt"):
    """Charge le template de prompt pour le LLM"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, prompt_file)
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
            print(f"✅ Prompt chargé depuis : {prompt_path}")
            return prompt_content
    except FileNotFoundError:
        print(f"⚠️ Fichier {prompt_path} introuvable. Utilisation d'un prompt par défaut.")
        return """Analyse le CV suivant et extrais les informations au format JSON exact :

{cv_text}

Retourne UNIQUEMENT un JSON valide avec cette structure :
{
  "first_name": "",
  "last_name": "",
  "full_name": "",
  "email": "",
  "phone_number": "",
  "technical_skills": [],
  "secondary_skills": [],
  "soft_skills": [],
  "languages": [{"language": "", "level": ""}],
  "educations": [{"title": "", "institution": "", "start_date": "", "end_date": "", "description": ""}],
  "experiences": [{"title": "", "company": "", "start_date": "", "end_date": "", "missions": "", "technical_skills_used": [], "soft_skills_used": []}],
  "interests": [],
  "summary": ""
}"""


# ---------------------------------------------------
# Extraction LLM
# ---------------------------------------------------
def extract_cv_data_with_llm(cv_text):
    """Envoie le CV au LLM et retourne les données structurées"""
    prompt_template = load_prompt()
    prompt = prompt_template.replace("{cv_text}", cv_text)

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        content = response.choices[0].message.content.strip()
        
        # Nettoyer la réponse si elle contient des marqueurs markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON : {e}")
        print(f"📄 Réponse brute du LLM :\n{content}\n")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'appel au LLM : {e}")
        return None


# ---------------------------------------------------
# Gestion ID incrémental
# ---------------------------------------------------
def load_existing_data(json_file):
    """Charge les données existantes du fichier JSON"""
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️ Erreur de lecture du JSON existant : {e}")
            backup_file = f"{json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(json_file, backup_file)
            print(f"📦 Fichier corrompu sauvegardé dans : {backup_file}")
            return []
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture du fichier : {e}")
            return []
    return []


def get_next_ids(json_file):
    """Retourne les prochains cv_id & candidate_id (format CAND-001, PERS-001)"""
    data = load_existing_data(json_file)

    if not data:
        return 1, 1

    cv_numbers = []
    candidate_numbers = []
    
    for item in data:
        try:
            if "cv_id" in item and item["cv_id"]:
                cv_num = int(item["cv_id"].split("-")[1])
                cv_numbers.append(cv_num)
            if "candidate_id" in item and item["candidate_id"]:
                cand_num = int(item["candidate_id"].split("-")[1])
                candidate_numbers.append(cand_num)
        except (IndexError, ValueError) as e:
            print(f"⚠️ ID malformé détecté : {e}")
            continue

    last_cv = max(cv_numbers) if cv_numbers else 0
    last_candidate = max(candidate_numbers) if candidate_numbers else 0

    return last_cv + 1, last_candidate + 1


# ---------------------------------------------------
# Compléter structure JSON obligatoire
# ---------------------------------------------------
def ensure_json_structure(cv_data, job_title=None):
    """Complète la structure JSON avec les champs manquants"""
    template = {
        "cv_id": None,
        "candidate_id": None,
        "source_email_id": None,
        "application_datetime": None,
        "job_applied_for": job_title,
        "first_name": None,
        "last_name": None,
        "full_name": None,
        "email": None,
        "phone_number": None,
        "technical_skills": [],
        "secondary_skills": [],
        "soft_skills": [],
        "languages": [],
        "educations": [],
        "experiences": [],
        "interests": [],
        "summary": None
    }
    
    for key, default in template.items():
        if key not in cv_data:
            cv_data[key] = default
    
    return cv_data

# ---------------------------------------------------
# Réorganisation du JSON (ordre des champs)
# ---------------------------------------------------
def reorder_json_fields(data):
    from collections import OrderedDict

    first_fields = [
        "cv_id",
        "candidate_id",
        "source_email_id",
        "application_datetime",
        "job_applied_for"
    ]

    ordered = OrderedDict()

    # Ajouter les champs prioritaires
    for field in first_fields:
        ordered[field] = data.get(field, None)

    # Ajouter les autres champs renvoyés par le LLM
    for key, value in data.items():
        if key not in first_fields:
            ordered[key] = value

    return ordered


# ---------------------------------------------------
# Sauvegarde JSON
# ---------------------------------------------------
def append_candidate_to_json(candidate_data, json_file):
    """Ajoute un candidat au fichier JSON sans écraser les données existantes"""
    data = load_existing_data(json_file)
    data.append(candidate_data)

    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Candidat {candidate_data['candidate_id']} ajouté au fichier JSON.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'écriture dans {json_file}: {e}")
        return False


# ---------------------------------------------------
# Vérification si l'email a déjà été traité
# ---------------------------------------------------
def is_email_already_processed(email_id, json_file):
    """Vérifie si un email a déjà été traité"""
    data = load_existing_data(json_file)
    return any(item.get("source_email_id") == email_id for item in data)


# ---------------------------------------------------
# Traitement Gmail + Extraction CV avec filtre par poste
# ---------------------------------------------------
def process_cvs(target_job_title=None, max_emails=50):
    """
    Traite les emails Gmail contenant des CV
    
    Args:
        target_job_title: Le poste à filtrer (ex: "Statisticien")
        max_emails: Nombre maximum d'emails à analyser
    """
    print("🚀 Démarrage de l'extraction des CV...")
    
    if not target_job_title:
        print("❌ ERREUR : Un poste doit être spécifié pour le traitement")
        return
    
    # Créer les chemins de sortie dynamiques
    cv_folder, json_file = create_output_paths(target_job_title)
    
    print(f"🎯 Poste ciblé : {target_job_title}")
    print(f"📁 Dossier CV : {cv_folder}")
    print(f"📄 Fichier JSON : {json_file}")
    print()
    
    service = get_gmail_service()
    print("✅ Connexion à Gmail réussie")

    results = service.users().messages().list(userId="me", maxResults=max_emails).execute()
    messages = results.get("messages", [])
    
    if not messages:
        print("📭 Aucun email trouvé.")
        return

    print(f"📧 {len(messages)} emails à analyser...\n")
    cv_count = 0
    filtered_out = 0

    for idx, msg in enumerate(messages, 1):
        print(f"--- Email {idx}/{len(messages)} ---")
        
        try:
            msg_data = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'email : {e}")
            continue

        # Vérifier si l'email a déjà été traité
        if is_email_already_processed(msg["id"], json_file):
            print(f"⏭️ Email {msg['id']} déjà traité, ignoré.\n")
            continue

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])

        # Récupérer les métadonnées de l'email
        sender_full = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
        sender_email = parseaddr(sender_full)[1]
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
        
        print(f"De : {sender_email}")
        print(f"Sujet : {subject}")

        # Extraire le poste depuis l'objet de l'email
        email_job_title = extract_job_title_from_subject(subject)
        
        if email_job_title:
            print(f"💼 Poste détecté : {email_job_title}")
        else:
            print("⚠️ Aucun poste détecté dans l'objet de l'email")

        # Filtrer par poste
        if not email_job_title:
            print(f"⏭️ Email ignoré : aucun poste détecté dans l'objet\n")
            filtered_out += 1
            continue
        
        if not job_titles_match(email_job_title, target_job_title):
            print(f"⏭️ Email ignoré : poste '{email_job_title}' ne correspond pas à '{target_job_title}'\n")
            filtered_out += 1
            continue
        
        print(f"✅ Poste correspondant ! Traitement du CV...")

        date_header = next((h["value"] for h in headers if h["name"].lower() == "date"), None)
        try:
            application_datetime = datetime.strptime(date_header[:-6], "%a, %d %b %Y %H:%M:%S").isoformat()
        except:
            application_datetime = datetime.now().isoformat()

        # Traiter les pièces jointes
        parts = payload.get("parts", [])
        if not parts:
            parts = [payload]

        cv_found = False
        for part in parts:
            filename = part.get("filename", "")
            body = part.get("body", {})
            
            if not filename:
                continue
                
            if filename.lower().endswith((".pdf", ".docx")) and "attachmentId" in body:
                cv_found = True
                print(f"📎 Pièce jointe trouvée : {filename}")

                try:
                    attachment = service.users().messages().attachments().get(
                        userId="me", messageId=msg["id"], id=body["attachmentId"]
                    ).execute()

                    file_data = base64.urlsafe_b64decode(attachment["data"])
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(cv_folder, safe_filename)

                    with open(filepath, "wb") as f:
                        f.write(file_data)

                    print(f"💾 CV téléchargé : {filepath}")

                    cv_text = extract_text(filepath)
                    
                    if not cv_text or len(cv_text) < 50:
                        print(f"⚠️ Texte extrait trop court ou vide, CV ignoré.\n")
                        continue

                    print(f"📄 Texte extrait : {len(cv_text)} caractères")

                    print("🤖 Envoi au LLM pour analyse...")
                    cv_data = extract_cv_data_with_llm(cv_text)
                    
                    if not cv_data:
                        print("⚠️ Impossible d'extraire les données du CV.\n")
                        continue

                    # Compléter la structure JSON avec le poste
                    cv_data = ensure_json_structure(cv_data, email_job_title)

                    # Générer les IDs uniques
                    next_cv, next_candidate = get_next_ids(json_file)
                    cv_data["cv_id"] = f"CAND-{next_cv:03d}"
                    cv_data["candidate_id"] = f"PERS-{next_candidate:03d}"
                    cv_data["source_email_id"] = msg["id"]
                    cv_data["application_datetime"] = application_datetime

                    print(f"🆔 IDs générés : {cv_data['cv_id']} / {cv_data['candidate_id']}")

                    cv_data = reorder_json_fields(cv_data)
                    if append_candidate_to_json(cv_data, json_file):
                        cv_count += 1
                        print(f"✅ Candidat {cv_data['full_name'] or 'Inconnu'} ajouté avec succès\n")
                    else:
                        print("❌ Échec de la sauvegarde\n")

                except Exception as e:
                    print(f"❌ Erreur lors du traitement de la pièce jointe : {e}\n")
                    continue

        if not cv_found:
            print("📭 Aucun CV trouvé dans cet email\n")

    print(f"\n{'='*60}")
    print(f"🎉 Extraction terminée !")
    print(f"📊 {cv_count} CV(s) traité(s) avec succès pour le poste : {target_job_title}")
    print(f"🔍 {filtered_out} email(s) filtré(s) (poste non correspondant)")
    print()
    print(f"📁 Organisation des fichiers :")
    print(f"   ├─ {cv_folder}")
    print(f"   └─ {json_file}")
    print(f"{'='*60}")


# ---------------------------------------------------
# MAIN avec interface utilisateur
# ---------------------------------------------------
if __name__ == "__main__":
    try:
        print("="*60)
        print("🎯 EXTRACTEUR DE CV PAR POSTE")
        print("="*60)
        print()
        
        # Demander le poste à filtrer (OBLIGATOIRE)
        while True:
            target_job = input("📝 Entrez le poste à filtrer (ex: Statisticien) : ").strip()
            if target_job:
                break
            print("❌ Le poste est obligatoire. Veuillez entrer un poste.\n")
        
        print(f"✅ Poste sélectionné : {target_job}")
        
        # Demander le nombre d'emails à analyser
        max_emails_input = input("📧 Nombre maximum d'emails à analyser (défaut: 50) : ").strip()
        max_emails = int(max_emails_input) if max_emails_input.isdigit() else 50
        
        print()
        print("🚀 Démarrage du traitement...")
        print()
        
        process_cvs(target_job_title=target_job, max_emails=max_emails)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()