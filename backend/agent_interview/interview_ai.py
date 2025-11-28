def generate_questionnaire(candidate: dict, offer: dict, n: int = 5, priority: str = "VERY_HIGH") -> list:
    """Génère une liste de questions d'entretien ciblées pour un candidat.

    Args:
        candidate: dict contenant au moins la clé 'skills' -> list de compétences détectées.
        offer: dict contenant au moins la clé 'needs' -> list de compétences/contraintes de l'offre.
        n: nombre maximal de questions à générer pour la priorité donnée.
        priority: niveau de priorité à filtrer ('VERY_HIGH' signale questions très ciblées).

    Retourne:
        list de chaînes (questions).
    """
    skills = set()
    needs = set()

    # Extraire skills depuis les structures les plus courantes
    if isinstance(candidate, dict):
        skills = set(candidate.get("skills") or candidate.get("competences") or [])
    if isinstance(offer, dict):
        needs = set(offer.get("needs") or offer.get("requirements") or offer.get("besoins") or [])

    questions = []

    # 1) Questions pour compétences détectées et demandées (intersection)
    common = list(skills & needs)
    for s in common:
        if len(questions) >= n:
            break
        questions.append(f"Pouvez-vous décrire une expérience concrète où vous avez utilisé '{s}' ? Quels étaient les enjeux et les résultats ?")

    # 2) Si on a encore de la place, poser des questions sur les compétences fortes du candidat non demandées
    if len(questions) < n and skills:
        extra = [s for s in skills if s not in common]
        for s in extra:
            if len(questions) >= n:
                break
            questions.append(f"Parlez-nous d'une réalisation marquante en lien avec '{s}'. Quelles méthodes avez-vous employées ?")

    # 3) Si l'offre demande des compétences que le candidat n'a pas, poser des questions d'adaptation
    if len(questions) < n and needs:
        missing = [s for s in needs if s not in skills]
        for s in missing:
            if len(questions) >= n:
                break
            questions.append(f"L'offre mentionne '{s}'. Comment aborderiez-vous ce sujet si vous deviez le prendre en charge ? (formation rapide, approche, priorités)")

    # 4) Compléments comportementaux / culturels si besoin
    if len(questions) < n:
        questions.append("Donnez un exemple d'une situation difficile au travail et comment vous l'avez résolue.")
    if len(questions) < n:
        questions.append("Comment vous organisez-vous pour monter en compétence rapidement sur un sujet technique inconnu ?")

    # Respecter la limite n
    return questions[:n]


if __name__ == "__main__":
    # Petit test local
    cand = {"skills": ["Python", "Analyse de données", "SQL"]}
    off = {"needs": ["SQL", "Machine Learning", "Communication"]}
    q = generate_questionnaire(cand, off, n=5)
    for i, qq in enumerate(q, 1):
        print(i, qq)