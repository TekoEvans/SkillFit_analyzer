# agent_matching/run_matching.py
"""
Script principal pour lancer l'agent Matching.

Usage:
    python run_matching.py --offer data/offer.json --cvs data/cvs.json --top_n 3 --output_dir outputs/
"""
import argparse
import json
from matcher import run_matching, save_results


def main():
    # Arguments
    parser = argparse.ArgumentParser(description="Agent Matching - SKILLFIT ANALYZER")
    parser.add_argument("--offer", required=True, help="Fichier JSON de l'offre")
    parser.add_argument("--cvs", required=True, help="Fichier JSON des CV")
    parser.add_argument("--top_n", type=int, required=True, help="Nombre de candidats à retenir")
    parser.add_argument("--output_dir", required=True, help="Dossier de sortie")
    args = parser.parse_args()
    
    # Charger les données
    print("Chargement des fichiers...")
    
    with open(args.offer, "r", encoding="utf-8") as f:
        offer = json.load(f)
    print(f"  Offre: {offer.get('offer_title', 'N/A')}")
    
    with open(args.cvs, "r", encoding="utf-8") as f:
        cvs = json.load(f)
    print(f"  CV: {len(cvs)} candidats")
    
    # Lancer le matching
    output = run_matching(offer, cvs, args.top_n)

    # Sauvegarder les résultats
    print("Sauvegarde des résultats...")
    save_results(output, args.output_dir)
    
    print("\n=== TERMINÉ ===")


if __name__ == "__main__":
    main()

