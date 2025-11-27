import json
from email_collector.llm_client import extract_cv_data_with_llm

def test_extract_cv_data_with_llm(monkeypatch):
    fake_json = {
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe"
    }

    class FakeResponse:
        choices = [type("obj", (), {"message": type("obj2", (), {"content": json.dumps(fake_json)})})]

    def fake_create(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("email_collector.llm_client.client.chat.completions.create", fake_create)

    result = extract_cv_data_with_llm("Fake CV content")
    assert result["full_name"] == "John Doe"
