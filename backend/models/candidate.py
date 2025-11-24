

class Candidate:
    """Objet représentant une offre candidat."""

    def __init__(self, name: str, surname: str, email :str, number: str):
        self.name = name
        self.surname = surname
        self.email = email
        self.number = number
        

    def __repr__(self):
        return f"<Applicant : Name={self.name} surname='{self.surname}' number='{self.number}'>"