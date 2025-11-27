import pytest
from email_collector.text_extract import extract_text

def test_extract_text_pdf(monkeypatch):
    def fake_pdf(path):
        return "Sample PDF text"
    monkeypatch.setattr("email_collector.text_extract.extract_text_from_pdf", fake_pdf)
    assert extract_text("hello.pdf") == "Sample PDF text"

def test_extract_text_docx(monkeypatch):
    def fake_docx(path):
        return "Sample DOCX text"
    monkeypatch.setattr("email_collector.text_extract.extract_text_from_docx", fake_docx)
    assert extract_text("hello.docx") == "Sample DOCX text"

def test_extract_text_unknown():
    assert extract_text("file.txt") == ""
