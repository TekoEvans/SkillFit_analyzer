# test_annonces_extractor.py

from annonces_extractor import clean_pdf_text

def test_clean_pdf_text_simple():
    input_text = "Bonjour   le   monde\n\nCeci   est un   test !"
    result = clean_pdf_text(input_text)

    assert "  " not in result     # Il ne doit plus rester de doubles espaces
    assert "\n\n" not in result   # Pas d'espaces multiples
    assert "Bonjour le monde" in result
