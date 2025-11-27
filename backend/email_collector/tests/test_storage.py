import json
from email_collector.storage import get_next_ids, append_candidate_to_json

def test_get_next_ids(tmp_path, monkeypatch):
    json_file = tmp_path / "candidates.json"
    json_file.write_text(json.dumps([
        {"cv_id": "CAND-001", "candidate_id": "PERS-001"},
        {"cv_id": "CAND-002", "candidate_id": "PERS-003"},
    ]))

    cv, cand = get_next_ids(str(json_file))
    assert cv == 3
    assert cand == 4

def test_append_candidate_to_json(tmp_path):
    json_file = tmp_path / "candidates.json"
    data = {"cv_id": "CAND-001", "candidate_id": "PERS-001"}
    
    append_candidate_to_json(data, str(json_file))
    saved = json.loads(json_file.read_text())

    assert saved[0]["cv_id"] == "CAND-001"
