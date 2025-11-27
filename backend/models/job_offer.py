class JobOffer:
    """Objet représentant une offre d'emploi."""

    def __init__(self,
                 title: str,
                 description: str,
                 responsibilities: list,
                 skills: list,
                 location: str,
                 experience: str,
                 contact_email: str,
                 full_text: str =None,
                 offer_id: str = None,
                 filename: str = None,
                 offer_date: str = None,
                 created_at: str = None,
                 updated_at: str = None):

        self.offer_id = offer_id
        self.title = title
        self.description = description
        self.responsibilities = responsibilities or []
        self.skills = skills or []
        self.location = location
        self.experience = experience
        self.contact_email = contact_email
        self.full_text = full_text
        self.filename = filename
        self.offer_date = offer_date
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return f"<JobOffer id={self.offer_id} title='{self.title}' location='{self.location}'>"
