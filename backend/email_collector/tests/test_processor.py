from email_collector.processor import extract_job_title_from_subject

def test_extract_job_title_from_subject():
    s = "Candidature — Data Analyst — Jean Dupont"
    assert extract_job_title_from_subject(s) == "Data Analyst"

    s2 = "Candidature - Statisticien - Durand"
    assert extract_job_title_from_subject(s2) == "Statisticien"

    assert extract_job_title_from_subject("Hello world") is None
