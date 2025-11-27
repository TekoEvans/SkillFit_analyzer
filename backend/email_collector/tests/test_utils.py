import pytest
from email_collector.utils import normalize_job_title, job_titles_match

def test_normalize_job_title():
    assert normalize_job_title("Statisticien Débutant") == "statisticien debutant"
    assert normalize_job_title("  DATA   Analyst  ") == "data analyst"
    assert normalize_job_title("Économétricien") == "econometricien"

def test_job_titles_match():
    assert job_titles_match("Statisticien débutant", "Statisticien")
    assert job_titles_match("Data Analyst", "analyst")
    assert not job_titles_match("Développeur Python", "Statisticien")
