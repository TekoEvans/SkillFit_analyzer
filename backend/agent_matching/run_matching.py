# -*- coding: utf-8 -*-
# agent_matching/main.py
import json
from pathlib import Path
from backend.agent_matching.matcher import run_matching, save_results


# def load_json_file(filepath: str):
#     """Charge un fichier JSON."""
#     with open(filepath, "r", encoding="utf-8") as f:
#         return json.load(f)


def matching(offer_path,cv_path,top_n):
    """Point d'entree principal de l'agent matching."""
    print("\n" + "="*60)
    print("  AGENT MATCHING - D-ZONE")
    print("="*60 + "\n")

    # 1. Charger les donnees d'entree
    print("Chargement des donnees...")

    # Charger l'offre
    with open(offer_path, "r", encoding="utf-8") as f:
        offer = json.load(f)

    # offer = load_json_file("data/offer.json")
    print(f"  - Offre chargee: {offer.get('offer_title', 'N/A')}")

    # Charger les CVs
    with open(cv_path, "r", encoding="utf-8") as f:
        cvs = json.load(f)
    
    print(f"  - {len(cvs)} CV(s) charge(s)")

    # Parametre : nombre de candidats VERY_HIGH a retenir
    TOP_N = top_n
    print(f"  - Top N candidats a retenir: {TOP_N}\n")

    # 2. Executer le matching
    results = run_matching(offer, cvs, top_n=TOP_N)

    # 3. Sauvegarder les resultats
    print("\nSauvegarde des resultats...")
    BASE_DIR = Path(__file__).resolve().parent
    save_results(results, output_dir=Path(BASE_DIR)/"outputs")
    

    # 4. Afficher un resume
    print("\n" + "="*60)
    print("  RESUME FINAL")
    print("="*60)
    print(f"Candidats retenus: {len(results['candidates_retained'])}")
    print(f"Candidats non retenus: {len(results['candidates_non_retained'])}")
    print("\nLes resultats sont disponibles dans le dossier 'outputs/'")
    print("="*60 + "\n")


if __name__ == "__main__":
    # matching(r"E:\All Evans\cours HETIC\MASRER  DATA & IA  2\Creation d'un agent\SkillFit_analyzer\backend\agent_offres\outputs\annonce_statisticien.json",r"E:\All Evans\cours HETIC\MASRER  DATA & IA  2\Creation d'un agent\SkillFit_analyzer\backend\email_collector\candidates\candidates_statisticien_20251127.json",4)
    pass