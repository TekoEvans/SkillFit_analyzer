from candidate import Candidate
from job_offer import JobOffer

class Application:
    """Objet représentant une candidature."""

    def __init__(self, candidate: Candidate, job_offer: JobOffer):
        self.candidate = candidate
        self.job_offer = job_offer
        
     
        

    def __repr__(self):
        return f"<Application de : {self.candidate.name}' au poste de' {self.job_offer.title}>"