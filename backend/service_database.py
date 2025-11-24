import sqlite3
from datetime import datetime, timezone
from typing import List
from models.job_offer import *

DB_PATH = "rh_jobs.db"



class JobOfferRepository:
    """Gestion des opérations CRUD sur les offres d'emploi."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        print("="*10)
        print("INITIALISATION DE LA BASE DE DONNEE RH")
        print("="*10)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                    CREATE TABLE IF NOT EXISTS job_offers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        department TEXT NOT NULL,
                        description TEXT NOT NULL,
                        location TEXT,
                        salary TEXT,
                        status INTEGER DEFAULT 1 ,
                        file_path TEXT ,
                        created_at TEXT NOT NULL,
                        updated_at TEXT
                )
                """
            )
            print("la tables des offres a ete cree")
            conn.commit()

    def add(self, offer: JobOffer) -> int:
        offer.created_at = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO job_offers (title, department, description, location, salary, status, created_at,file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    offer.title,
                    offer.department,
                    offer.description,
                    offer.location,
                    offer.salary,
                    offer.status,
                    offer.created_at,
                    offer.file_path
                ),
            )
            conn.commit()
            offer.id = cur.lastrowid
            return f'OFFRE_00{offer.id}'
        

    def get(self, offer_id: int) -> JobOffer:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM job_offers WHERE id = ?", (offer_id,))
            row = cur.fetchone()
            if not row:
                return None
            return JobOffer(
                title=row[1],
                department=row[2],
                description=row[3],
                location=row[4],
                salary=row[5],
                status=row[6],
                offer_id=row[0],
                created_at=row[7],
                file_path=row[8],
                updated_at=row[9],
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
                        title=r[1], department=r[2], description=r[3],
                        location=r[4], salary=r[5], status=r[6],
                        file_path=r[8],
                        offer_id=r[0], created_at=r[7], updated_at=r[9]
                    ) for r in rows
                    ]
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM job_offers ORDER BY id DESC")
            rows = cur.fetchall()
            return [
                    JobOffer(
                        title=r[1], department=r[2], description=r[3],
                        location=r[4], salary=r[5], status=r[6],
                        file_path=r[7], offer_id=r[0], created_at=r[8], updated_at=r[9]
                    ) for r in rows
                    ]

    def update(self, offer: JobOffer) -> bool:
        offer.updated_at = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE job_offers SET
                    title = ?, department = ?, description = ?,
                    location = ?, salary = ?, status = ?, file_path = ? , updated_at = ?
                WHERE id = ?
                """,
                (
                    offer.title,
                    offer.department,
                    offer.description,
                    offer.location,
                    offer.salary,
                    offer.status,
                    offer.updated_at,
                    offer.id,
                ),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete(self, offer_id: int) -> bool:
        """Supprime une offre après confirmation et vérifie son existence."""
        # Vérifier si l'offre existe
        existing = self.get(offer_id)
        if not existing:
            print(f"❌ L'offre avec ID {offer_id} n'existe pas.")
            return False


        # Demander confirmation utilisateur
        confirmation = input(f"Êtes‑vous sûr de vouloir supprimer l'offre {offer_id} (oui/non) ? ").strip().lower()
        if confirmation not in ["oui", "o", "yes", "y"]:
            print("❎ Suppression annulée par l'utilisateur.")
            return False


        # Suppression si confirmé
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
    # offer = JobOffer(
    #     title="Développeur Python",
    #     department="Informatique",
    #     description="Développement interne",
    #     location="Paris",
    #     salary="45-55k€",
    #     file_path='/offrers_pdf/annonce_data.pdf'
    # )

    # new_id = repo.add(offer)
    # print("Offre créée, id =", new_id)

    # # # Liste
    # print("Liste des offres :")
    # for o in repo.list():
    #     print(o)

    # Modification
    # offer.status = "fermée"
    # repo.update(offer)

    # Suppression
    repo.delete(1)
