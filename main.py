import streamlit as st
import os
from pathlib import Path

# Import du backend (important : fonctionner dans le dossier inference/)
from backend.models.job_offer import JobOffer
from backend.service_database import JobOfferRepository


BASE_DIR =  os.path.join(Path(__file__).resolve().parent, "backend\email_collector\candidates\candidates_finance_20251127.json")
print(BASE_DIR)

