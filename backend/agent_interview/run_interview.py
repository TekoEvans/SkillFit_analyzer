import json
import os
from pathlib import Path

from interview_ai import generate_questionnaire


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    # Lire les données depuis les autres agents (lecture seule)
    base_matching = Path(__file__).resolve().parents[1] / "agent_matching"
    base_email = Path(__file__).resolve().parents[1] / "email_collector"
    base_offres = Path(__file__).resolve().parents[2] / "offres_pdf"
    
    retained_path = base_matching / "outputs" / "candidates_retained.json"
    # Chercher les fichiers JSON de candidats
    candidates_json_files = list((base_email / "candidates").glob("candidates_*.json"))
    offer_path = base_offres / "annonce_statisticien.json"

    # Charger les données
    retained = load_json(retained_path)
    offer = load_json(offer_path)
    
    # Merger tous les candidats depuis EmailCollector
    candidates_pool = []
    for cand_file in candidates_json_files:
        candidates_pool.extend(load_json(cand_file))
    
    # Créer les répertoires de sortie UNIQUEMENT dans agent_interview
    out_dir = Path(__file__).resolve().parent / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    interview_fiches = []

    for retained_entry in retained:
        cv_id = retained_entry.get("cv_id")
        if not cv_id:
            continue
        
        # Trouver le candidat dans le pool EmailCollector
        email_candidate = None
        for cand in candidates_pool:
            if cand.get("cv_id") == cv_id:
                email_candidate = cand
                break
        
        if not email_candidate:
            print(f"⚠ Candidat {cv_id} introuvable dans EmailCollector, skip.")
            continue
        
        # Extraire les compétences
        candidate_skills = email_candidate.get("technical_skills", [])
        
        candidate_obj = {"cv_id": cv_id, "full_name": email_candidate.get("full_name"), "skills": candidate_skills}
        
        # Générer les questions d'entretien
        questions = generate_questionnaire(candidate_obj, offer, n=5, priority="VERY_HIGH")
        
        # Créer la fiche enrichie
        fiche = {
            "cv_id": cv_id,
            "candidate_info": {
                "full_name": email_candidate.get("full_name"),
                "first_name": email_candidate.get("first_name"),
                "last_name": email_candidate.get("last_name"),
                "email": email_candidate.get("email"),
                "phone_number": email_candidate.get("phone_number"),
                "technical_skills": email_candidate.get("technical_skills", []),
                "soft_skills": email_candidate.get("soft_skills", []),
                "educations": email_candidate.get("educations", []),
                "experiences": email_candidate.get("experiences", []),
                "summary": email_candidate.get("summary", ""),
                "interests": email_candidate.get("interests", []),
            },
            "matching_info": {
                "matching_score": retained_entry.get("matching_score"),
                "matching_level": retained_entry.get("matching_level"),
                "rationale": retained_entry.get("rationale"),
                "key_points": retained_entry.get("key_points", []),
                "application_datetime": retained_entry.get("application_datetime"),
            },
            "offer_info": {
                "title": offer.get("title"),
                "description": offer.get("description"),
                "responsibilities": offer.get("responsibilities", []),
                "skills_required": offer.get("skills", []),
                "location": offer.get("location"),
                "experience_required": offer.get("experience"),
                "contact_email": offer.get("contact_email"),
                "offer_date": offer.get("offer_date"),
            },
            "interview_questions": questions,
        }
        
        interview_fiches.append(fiche)
        
        # Écrire le fichier individuel dans outputs/
        out_file = out_dir / f"interview_fiche_{cv_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(fiche, f, ensure_ascii=False, indent=2)
        print(f"✓ {out_file}")
    
    # Écrire le résumé global
    summary_file = out_dir / "interview_fiches.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(interview_fiches, f, ensure_ascii=False, indent=2)
    print(f"\n✓ Résumé: {summary_file} ({len(interview_fiches)} candidats)")


if __name__ == "__main__":
    main()
