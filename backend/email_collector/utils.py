import re


def normalize_job_title(job_title):
    if not job_title:
        return ""

    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c'
    }

    jt = job_title.lower()
    for a, r in replacements.items():
        jt = jt.replace(a, r)

    jt = re.sub(r'\s+', ' ', jt).strip()
    return jt


def job_titles_match(subject_job, target_job):
    ns = normalize_job_title(subject_job)
    nt = normalize_job_title(target_job)
    if ns == nt:
        return True
    if nt in ns or ns in nt:
        return True
    return False


def extract_job_title_from_subject(subject):
    patterns = [r'Candidature\s*[—-]\s*([^—-]+)\s*[—-]', r'[—-]\s*([^—-]+)\s*[—-]']
    for pattern in patterns:
        match = re.search(pattern, subject or "", re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
