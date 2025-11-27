import os
import re
from datetime import datetime


MAIN_CANDIDATES_FOLDER = "candidates"
MAIN_CV_FOLDER = "cv_files"


def create_output_paths(job_title):
    script_dir = os.path.dirname(__file__)

    # Normaliser le titre du poste pour l'utiliser dans les noms de fichiers
    safe_job_title = (job_title or "").strip()

    safe_job_title = re.sub(r'[-\s]+', '_', safe_job_title).strip('_')
    # garder lettres/chiffres/espaces/tirets
    safe_job_title = re.sub(r'[^\w\s-]', '', safe_job_title)
    safe_job_title = re.sub(r'[-\s]+', '_', safe_job_title).strip('_')
    safe_job_title = safe_job_title.lower()

    date_str = datetime.now().strftime("%Y%m%d")

    cv_folder_name = f"cv_files_{safe_job_title}_{date_str}"
    json_file_name = f"candidates_{safe_job_title}_{date_str}.json"

    # Créer chemins relatifs au dossier du package
    base = script_dir
    cv_folder = os.path.join(base, MAIN_CV_FOLDER, cv_folder_name)
    json_file = os.path.join(base, MAIN_CANDIDATES_FOLDER, json_file_name)

    os.makedirs(cv_folder, exist_ok=True)
    os.makedirs(os.path.dirname(json_file), exist_ok=True)

    return cv_folder, json_file
