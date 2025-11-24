

class JobOffer:
    """Objet représentant une offre d'emploi."""

    def __init__(self, title: str, department: str, description: str,
                 location: str = None, salary: str = None,
                 status: int = 1, offer_id: int = None,
                 file_path: str = None,
                 created_at: str = None, updated_at: str = None):
        self.id = offer_id
        self.title = title
        self.department = department
        self.description = description
        self.file_path = file_path
        self.location = location
        self.salary = salary
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"<JobOffer id={self.id} title='{self.title}' dept='{self.department}' status='{self.status}'>"