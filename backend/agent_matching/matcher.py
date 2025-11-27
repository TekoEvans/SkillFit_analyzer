# agent_matching/matcher.py
import json
import csv
import os
from datetime import datetime
from llm_client import call_llm


def run_matching(offer: dict, cvs: list, top_n: int) -> dict:
    """
    Exécute le matching entre une offre et une liste de CV.
    
    Args:
        offer: Dictionnaire de l'offre (format D-Zone)
        cvs: Liste de dictionnaires CV (format D-Zone)
        top_n: Nombre max de candidats VERY_HIGH à retenir
    
    Returns:
        dict avec candidates_retained et candidates_non_retained
    """
    print(f"\n=== AGENT MATCHING ===")
    print(f"Offre: {offer.get('offer_title', 'N/A')}")
    print(f"Nombre de CV: {len(cvs)}")
    print(f"Top N: {top_n}\n")
    
    # 1. Analyser chaque CV
    results = []
    for i, cv in enumerate(cvs):
        name = cv.get("full_name") or f"{cv.get('first_name', '')} {cv.get('last_name', '')}".strip()
        print(f"  Analyse {i+1}/{len(cvs)}: {name}...")
        
        # Appel LLM
        decision = call_llm(offer, cv)
        
        # Stocker le résultat
        results.append({
            "cv": cv,
            "score": decision["matching_score"],
            "level": decision["matching_level"],
            "rationale": decision["rationale"],
            "key_points": decision.get("key_points", [])
        })
        
        print(f"    -> Score: {decision['matching_score']}, Niveau: {decision['matching_level']}")
    
    # 2. Filtrer les VERY_HIGH
    very_high = [r for r in results if r["level"] == "VERY_HIGH"]
    high = [r for r in results if r["level"] == "HIGH"]
    medium = [r for r in results if r["level"] == "MEDIUM"]
    
    # 3. Trier par date de candidature (plus ancien = prioritaire)
    very_high.sort(key=lambda r: r["cv"].get("application_datetime", ""))
    high.sort(key=lambda r: r["cv"].get("application_datetime", ""))
    medium.sort(key=lambda r: r["cv"].get("application_datetime", ""))
    
    # 4. Sélectionner les N premiers
    retained = very_high[:top_n]
    i=0
    while len(retained)<top_n and i < len(high):
        
        retained.append(high[i])
        i=+1
    while len(retained)<top_n and i < len(medium):
        
        retained.append(medium[i])
        i=+1    

    # 5. Les autres sont non retenus
    retained_cv_ids = {r["cv"]["cv_id"] for r in retained}
    non_retained = [r for r in results if r["cv"]["cv_id"] not in retained_cv_ids]
    
    print(f"\n=== RÉSULTAT ===")
    print(f"VERY_HIGH total: {len(very_high)}")
    print(f"Retenus: {len(retained)}")
    print(f"Non retenus: {len(non_retained)}\n")
    
    return {
        "offer": offer,
        "candidates_retained": retained,
        "candidates_non_retained": non_retained
    }


def save_results(output: dict, output_dir: str):
    """Sauvegarde les résultats en JSON et CSV."""
    os.makedirs(output_dir, exist_ok=True)
    
    offer = output["offer"]
    retained = output["candidates_retained"]
    non_retained = output["candidates_non_retained"]
    
    # 1. JSON des retenus
    retained_data = []
    for r in retained:
        cv = r["cv"]
        retained_data.append({
            "cv_id": cv.get("cv_id"),
            "full_name": cv.get("full_name") or f"{cv.get('first_name', '')} {cv.get('last_name', '')}".strip(),
            "email": cv.get("email"),
            "phone_number": cv.get("phone_number"),
            "offer_id": offer.get("offer_id"),
            "offer_title": offer.get("offer_title"),
            "matching_score": r["score"],
            "matching_level": r["level"],
            "application_datetime": cv.get("application_datetime"),
            "rationale": r["rationale"],
            "key_points": r["key_points"],
            "statut": "RETENU"
        })
    
    with open(f"{output_dir}/candidates_retained.json", "w", encoding="utf-8") as f:
        json.dump(retained_data, f, indent=2, ensure_ascii=False)
    print(f"  -> {output_dir}/candidates_retained.json")
    
    # 2. JSON des non retenus
    non_retained_data = []
    for r in non_retained:
        cv = r["cv"]
        non_retained_data.append({
            "cv_id": cv.get("cv_id"),
            "full_name": cv.get("full_name") or f"{cv.get('first_name', '')} {cv.get('last_name', '')}".strip(),
            "email": cv.get("email"),
            "phone_number": cv.get("phone_number"),
            "offer_id": offer.get("offer_id"),
            "matching_score": r["score"],
            "matching_level": r["level"],
            "application_datetime": cv.get("application_datetime"),
            "motif": r["rationale"],
            "statut": "NON RETENU"
        })
    
    with open(f"{output_dir}/candidates_non_retained.json", "w", encoding="utf-8") as f:
        json.dump(non_retained_data, f, indent=2, ensure_ascii=False)
    print(f"  -> {output_dir}/candidates_non_retained.json")
    
    # 3. CSV des retenus (pour Excel)
    with open(f"{output_dir}/candidates_retained.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["cv_id", "full_name", "email", "phone", "score", "level", "date_candidature", "statut"])
        for r in retained_data:
            writer.writerow([
                r["cv_id"], r["full_name"], r["email"], r["phone_number"],
                r["matching_score"], r["matching_level"], r["application_datetime"], "RETENU"
            ])
    print(f"  -> {output_dir}/candidates_retained.csv")
    
    # 4. CSV des non retenus
    with open(f"{output_dir}/candidates_non_retained.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["cv_id", "full_name", "email", "phone", "score", "level", "date_candidature", "motif"])
        for r in non_retained_data:
            writer.writerow([
                r["cv_id"], r["full_name"], r["email"], r["phone_number"],
                r["matching_score"], r["matching_level"], r["application_datetime"], r["motif"]
            ])
    print(f"  -> {output_dir}/candidates_non_retained.csv")
    
    # 5. Fiches individuelles pour chaque retenu
    sheets_dir = f"{output_dir}/fiches_candidats"
    os.makedirs(sheets_dir, exist_ok=True)
    for r in retained_data:
        filepath = f"{sheets_dir}/{r['cv_id']}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
    print(f"  -> {sheets_dir}/ ({len(retained_data)} fiches)")
