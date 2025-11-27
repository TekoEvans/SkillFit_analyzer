import os
import json
from datetime import datetime


def _read_json_file(json_file):
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError:
            backup_file = f"{json_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(json_file, backup_file)
            return []
        except Exception:
            return []
    return []


def load_existing_data(json_file):
    return _read_json_file(json_file)


def get_next_ids(json_file):
    data = _read_json_file(json_file)
    if not data:
        return 1, 1

    cv_numbers = []
    candidate_numbers = []
    for item in data:
        try:
            if "cv_id" in item and item["cv_id"]:
                cv_num = int(item["cv_id"].split("-")[1])
                cv_numbers.append(cv_num)
            if "candidate_id" in item and item["candidate_id"]:
                cand_num = int(item["candidate_id"].split("-")[1])
                candidate_numbers.append(cand_num)
        except Exception:
            continue

    last_cv = max(cv_numbers) if cv_numbers else 0
    last_candidate = max(candidate_numbers) if candidate_numbers else 0
    return last_cv + 1, last_candidate + 1


def ensure_json_structure(cv_data, job_title=None):
    template = {
        "cv_id": None,
        "candidate_id": None,
        "source_email_id": None,
        "application_datetime": None,
        "job_applied_for": job_title,
        "first_name": None,
        "last_name": None,
        "full_name": None,
        "email": None,
        "phone_number": None,
        "technical_skills": [],
        "secondary_skills": [],
        "soft_skills": [],
        "languages": [],
        "educations": [],
        "experiences": [],
        "interests": [],
        "summary": None
    }
    for key, default in template.items():
        if key not in cv_data:
            cv_data[key] = default
    return cv_data


def reorder_json_fields(data):
    from collections import OrderedDict

    first_fields = [
        "cv_id",
        "candidate_id",
        "source_email_id",
        "application_datetime",
        "job_applied_for"
    ]
    ordered = OrderedDict()
    for field in first_fields:
        ordered[field] = data.get(field, None)
    for key, value in data.items():
        if key not in first_fields:
            ordered[key] = value
    return ordered


def append_candidate_to_json(candidate_data, json_file):
    data = _read_json_file(json_file)
    data.append(candidate_data)
    try:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def is_email_already_processed(email_id, json_file):
    data = _read_json_file(json_file)
    return any(item.get("source_email_id") == email_id for item in data)
