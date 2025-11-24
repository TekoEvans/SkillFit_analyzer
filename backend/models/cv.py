from candidate import Candidate

class Cv:
    """Objet représentant un cv."""

    def __init__(self,title : str, candidate: Candidate, carateristics: object):
        self.candidate = candidate
        self.carateristics = carateristics
        self.title = title
     
        

    def __repr__(self):
        return f"<CV : {self.candidate.email}'>"