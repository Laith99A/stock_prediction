from stock_analyzer import ui
from stock_analyzer.companies import ABOUT, about
from stock_analyzer.fundamentals import parse_info
from stock_analyzer.universes import CATALOG


def test_every_catalog_stock_has_a_german_description():
    assert set(CATALOG) - set(ABOUT) == set()
    assert all(text and len(text) < 200 for text in ABOUT.values())


def test_about_prefers_german_text_and_falls_back_to_yahoo():
    text, german = about("AAPL", "Apple Inc. designs smartphones.")
    assert german and text == ABOUT["AAPL"]

    long_summary = "Example Corp makes useful things for many customers. " * 10
    text, german = about("XYZ.DE", long_summary, max_chars=120)
    assert not german and len(text) <= 120 and text.endswith(".")

    assert about("XYZ.DE", None) == ("", False)


def test_parse_info_reads_company_profile():
    f = parse_info("EX", {"longBusinessSummary": "Makes things.", "fullTimeEmployees": 1200,
                          "city": "Walldorf", "country": "Germany", "website": "www.example.com"})
    assert f.summary == "Makes things." and f.employees == 1200
    assert (f.city, f.country) == ("Walldorf", "Germany")
    assert f.website == "https://www.example.com"


def test_company_card_escapes_text_and_skips_empty_facts():
    card = ui.company_card("A & B", "Baut <Dinge>.", True, [("Sitz", "Berlin"), ("Mitarbeiter", "")],
                           "https://example.com")
    assert "A &amp; B" in card and "&lt;Dinge&gt;" in card
    assert "Berlin" in card and "Mitarbeiter" not in card and "https://example.com" in card
    assert "Yahoo" not in card

    assert "Yahoo Finance" in ui.company_card("X", "English text.", False, [])
    assert "javascript:" not in ui.company_card("X", "", True, [], "javascript:alert(1)")


def test_big_number_uses_german_short_scale():
    assert ui.big_number(1.2e12) == "1,2 Bio."
    assert ui.big_number(3.4e9) == "3,4 Mrd."
    assert ui.big_number(None) == "–"
