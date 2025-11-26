import os
import base64
from datetime import datetime

# Support both package-relative imports (when run as module) and direct execution
try:
    # Preferred when imported as package
    from .service import get_gmail_service
    from .paths import create_output_paths
    from .utils import extract_job_title_from_subject, job_titles_match
    from .text_extract import extract_text
    from .llm_client import extract_cv_data_with_llm
    from .storage import (
        is_email_already_processed,
        ensure_json_structure,
        get_next_ids,
        append_candidate_to_json,
        reorder_json_fields,
    )
except Exception:
    # Fallback for direct execution (python processor.py)
    import sys
    # repo root is three levels up from this file: /<repo>/backend/email_collector/processor.py
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Try to import using package path first (when running from repo root)
    try:
        from backend.email_collector.service import get_gmail_service
        from backend.email_collector.paths import create_output_paths
        from backend.email_collector.utils import extract_job_title_from_subject, job_titles_match
        from backend.email_collector.text_extract import extract_text
        from backend.email_collector.llm_client import extract_cv_data_with_llm
        from backend.email_collector.storage import (
            is_email_already_processed,
            ensure_json_structure,
            get_next_ids,
            append_candidate_to_json,
            reorder_json_fields,
        )
    except Exception:
        # Fallback to local module names (works when executed from package directory)
        from service import get_gmail_service
        from paths import create_output_paths
        from utils import extract_job_title_from_subject, job_titles_match
        from text_extract import extract_text
        from llm_client import extract_cv_data_with_llm
        from storage import (
            is_email_already_processed,
            ensure_json_structure,
            get_next_ids,
            append_candidate_to_json,
            reorder_json_fields,
        )


def process_cvs(target_job_title=None, max_emails=50, verbose=True):
    if not target_job_title:
        raise ValueError("target_job_title is required")

    if verbose:
        print("🚀 Démarrage du traitement (processor)...")

    cv_folder, json_file = create_output_paths(target_job_title)
    if verbose:
        print(f"📁 CV folder: {cv_folder}")
        print(f"📄 JSON file: {json_file}")
        print("🔌 Connexion à Gmail...")

    service = get_gmail_service()
    if verbose:
        print("✅ Connexion Gmail obtenue")

    if verbose:
        print(f"📧 Recherche jusqu'à {max_emails} messages")
    results = service.users().messages().list(userId="me", maxResults=max_emails).execute()
    messages = results.get("messages", [])

    cv_count = 0
    filtered_out = 0

    total = len(messages)
    for idx, msg in enumerate(messages, start=1):
        print(f"--- Email {idx}/{total} (id={msg.get('id')}) ---")
        try:
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        except Exception as e:
            print(f"❌ Erreur récupération email {msg.get('id')}: {e}")
            continue

        if is_email_already_processed(msg["id"], json_file):
            print(f"⏭️ Email {msg['id']} déjà traité — skip")
            continue

        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])

        sender_full = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
        print(f"De: {sender_full}")
        print(f"Sujet: {subject}")

        email_job_title = extract_job_title_from_subject(subject)
        if not email_job_title:
            print("⚠️ Aucun poste détecté dans l'objet — skip")
            filtered_out += 1
            continue

        print(f"💼 Poste détecté dans l'objet: {email_job_title}")
        if not job_titles_match(email_job_title, target_job_title):
            print(f"⏭️ Poste '{email_job_title}' ne correspond pas à '{target_job_title}' — skip")
            filtered_out += 1
            continue

        date_header = next((h["value"] for h in headers if h["name"].lower() == "date"), None)
        try:
            application_datetime = datetime.strptime(date_header[:-6], "%a, %d %b %Y %H:%M:%S").isoformat()
        except Exception:
            application_datetime = datetime.now().isoformat()

        parts = payload.get("parts", []) or [payload]
        cv_found = False

        for part in parts:
            filename = part.get("filename", "")
            body = part.get("body", {})
            if not filename:
                continue
            if filename.lower().endswith((".pdf", ".docx")) and "attachmentId" in body:
                cv_found = True
                print(f"📎 Pièce jointe trouvée: {filename}")
                try:
                    attachment = service.users().messages().attachments().get(userId="me", messageId=msg["id"], id=body["attachmentId"]).execute()
                    file_data = base64.urlsafe_b64decode(attachment.get("data", ""))
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_filename = f"{timestamp}_{filename}"
                    filepath = os.path.join(cv_folder, safe_filename)
                    with open(filepath, "wb") as f:
                        f.write(file_data)
                    print(f"💾 CV sauvegardé: {filepath}")

                    cv_text = extract_text(filepath)
                    if not cv_text or len(cv_text) < 50:
                        print("⚠️ Texte extrait trop court — skip")
                        continue

                    print(f"📄 Texte extrait ({len(cv_text)} caractères). Envoi au LLM...")
                    cv_data = extract_cv_data_with_llm(cv_text)
                    if not cv_data:
                        print("⚠️ LLM n'a pas renvoyé de données valides — skip")
                        continue

                    cv_data = ensure_json_structure(cv_data, email_job_title)
                    next_cv, next_candidate = get_next_ids(json_file)
                    cv_data["cv_id"] = f"CAND-{next_cv:03d}"
                    cv_data["candidate_id"] = f"PERS-{next_candidate:03d}"
                    cv_data["source_email_id"] = msg["id"]
                    cv_data["application_datetime"] = application_datetime

                    cv_data = reorder_json_fields(cv_data)
                    if append_candidate_to_json(cv_data, json_file):
                        cv_count += 1
                        print(f"✅ Candidat ajouté: {cv_data.get('full_name') or 'Inconnu'} ({cv_data['candidate_id']})")
                    else:
                        print("❌ Échec sauvegarde JSON")
                except Exception as e:
                    print(f"❌ Erreur processing piece jointe: {e}")
                    continue

        if not cv_found:
            print("📭 Aucun CV trouvé dans cet email")


    return {"processed": cv_count, "filtered": filtered_out, "cv_folder": cv_folder, "json_file": json_file}
