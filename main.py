import streamlit as st
import os

# Import du backend (important : fonctionner dans le dossier inference/)
from backend.models.job_offer import JobOffer
from backend.service_database import JobOfferRepository

def squares(n):
    for i in range(n):
        yield i * i


print(next(squares(4)))


