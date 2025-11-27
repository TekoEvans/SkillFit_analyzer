import sqlite3, json
from datetime import datetime, timezone
from typing import List, Optional
from backend.models.job_offer import JobOffer

DB_PATH = "rh_jobs.db"


class JobOfferRepository:
    """Gestion des opérations CRUD sur les offres d'emploi."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        print("=" * 10)
        print("INITIALISATION DE LA BASE DE DONNEE RH")
        print("=" * 10)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS job_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    responsibilities TEXT,      
                    skills TEXT,                
                    location TEXT,
                    experience TEXT,
                    contact_email TEXT,
                    full_text TEXT,
                    filename TEXT,
                    offer_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT
                )
                """
            )
            print("La table des offres a été créée")
            conn.commit()

    def add(self, offer: JobOffer) -> str:
        offer.created_at = datetime.now(timezone.utc).isoformat()
        offer.updated_at = offer.created_at
        
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO job_offers (
                    title, description, responsibilities, skills,
                    location, experience, contact_email, full_text, filename,
                    offer_date, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    offer.title,
                    offer.description,
                    offer.responsibilities,
                    json.dumps(offer.skills),
                    offer.location,
                    offer.experience,
                    offer.contact_email,
                    offer.full_text,
                    offer.filename,
                    offer.offer_date,
                    offer.created_at,
                    offer.updated_at,
                ),
            )
            conn.commit()
            offer.offer_id = cur.lastrowid
            offer.offer_id = f'OFFRE_00{offer.offer_id}'
            return offer.offer_id

    def get(self, offer_id: int) -> Optional[JobOffer]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM job_offers WHERE id = ?", (offer_id,))
            r = cur.fetchone()
            if not r:
                return None
            return JobOffer(
               offer_id=r[0],
                    title=r[1],
                    description=r[2],
                    responsibilities=r[3],
                    skills=r[4],
                    location=r[5],
                    experience=r[6],
                    contact_email=r[7],
                    full_text=r[8],
                    filename=r[9],
                    offer_date=r[10],
                    created_at=r[11],
                    updated_at=r[12]
            )

    def list(self) -> List[JobOffer]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM job_offers ORDER BY id DESC")
            rows = cur.fetchall()

            if not rows:
                print("📭 Aucune offre d'emploi disponible.")
                return []

            return [
                JobOffer(
                   
                    offer_id=r[0],
                    title=r[1],
                    description=r[2],
                    responsibilities=r[3],
                    skills=r[4],
                    location=r[5],
                    experience=r[6],
                    contact_email=r[7],
                    full_text=r[8],
                    filename=r[9],
                    offer_date=r[10],
                    created_at=r[11],
                    updated_at=r[12]
                ) for r in rows
            ]

    def update(self, offer: JobOffer) -> bool:
        offer.updated_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE job_offers SET
                    title = ?, description = ?, responsibilities = ?, skills = ?,
                    location = ?, experience = ?, contact_email = ?, full_text = ?,
                    filename = ?, offer_date = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    offer.title,
                    offer.description,
                    offer.responsibilities,
                    offer.skills,
                    offer.location,
                    offer.experience,
                    offer.contact_email,
                    offer.full_text,
                    offer.filename,
                    offer.offer_date,
                    offer.updated_at,
                    offer.offer_id,
                ),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete(self, offer_id: int) -> bool:
        """Supprime une offre après confirmation et vérifie son existence."""
        existing = self.get(offer_id)
        if not existing:
            print(f"❌ L'offre avec ID {offer_id} n'existe pas.")
            return False

        confirmation = input(
            f"Êtes-vous sûr de vouloir supprimer l'offre {offer_id} (oui/non) ? "
        ).strip().lower()
        if confirmation not in ["oui", "o", "yes", "y"]:
            print("❎ Suppression annulée par l'utilisateur.")
            return False

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM job_offers WHERE id = ?", (offer_id,))
            conn.commit()
            if cur.rowcount > 0:
                print(f"🗑️ Offre {offer_id} supprimée avec succès.")
                return True
            else:
                print("⚠️ Erreur : suppression impossible.")
                return False


if __name__ == "__main__":
    repo = JobOfferRepository()

    # Création d'une offre
    offer = JobOffer(
                    title="Chef de Projet Digital",
                    description="Pilotage de projets web et mobile pour clients grands comptes",
                    responsibilities="Gestion d'équipe, planification, relation client",
                    skills="Agile, Scrum, JIRA, MS Project",
                    location="location",
                    experience=5,
                    contact_email="rh@cabinet-conseil.fr",
                    filename="pdf",  # Extrait juste le nom du fichier
                    # filename=pdf_path.split('/')[-1],  # Extrait juste le nom du fichier
                    offer_date="2025-02-01"
                    )
    new_id = repo.add(offer)
    print("Offre créée, id =", new_id)

    # Liste
    print("Liste des offres :")
    for o in repo.list():
        print(o)

    # Suppression
# repo.delete(1)