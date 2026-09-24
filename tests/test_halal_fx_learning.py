import pytest

from stock_analyzer.fundamentals import Fundamentals
from stock_analyzer.fx import DEMO_RATES, fx_tickers, to_eur
from stock_analyzer.glossary import TERMS
from stock_analyzer.halal import CHECK, HALAL, NOT_HALAL, business_screen, check
from stock_analyzer.learning import POOL, quiz, word_of_the_day
from stock_analyzer.universes import CATALOG, CHINA, UNIVERSES, flag, market_of


def funda(ticker, de, sector=None, industry=None):
    return Fundamentals(ticker, debt_to_equity=de, sector=sector, industry=industry)


@pytest.mark.parametrize(("ticker", "category"), [
    ("ABI.BR", "alkohol"), ("PM", "tabak"), ("RHM.DE", "waffen"), ("LMT", "waffen"), ("0027.HK", "gluecksspiel"),
    ("JPM", "zinsen"), ("DBK.DE", "zinsen"), ("ALV.DE", "versicherung"), ("2318.HK", "versicherung"),
])
def test_forbidden_businesses_are_not_halal(ticker, category):
    result = check(ticker, funda(ticker, 0.1))
    assert result.status == NOT_HALAL
    assert business_screen(ticker, None, None) == (NOT_HALAL, category)


def test_debt_rule_is_33_percent_of_equity():
    assert check("AAPL", funda("AAPL", 0.33)).status == HALAL
    too_high = check("AAPL", funda("AAPL", 0.34))
    assert too_high.status == NOT_HALAL and "0,34 > 0,33" in too_high.debt_reason
    assert check("AAPL", funda("AAPL", -0.5)).status == NOT_HALAL  # negative equity
    unknown = check("AAPL", funda("AAPL", None))
    assert unknown.status == CHECK and unknown.label == "Prüfen"


def test_grey_areas_and_unknown_stocks():
    assert check("NFLX", funda("NFLX", 0.1)).status == CHECK
    assert check("COIN", funda("COIN", 0.1)).status == CHECK
    # stocks outside the lists fall back to the Yahoo industry
    assert business_screen("XYZ", "Consumer Defensive", "Beverages - Brewers")[0] == NOT_HALAL
    assert business_screen("XYZ", "Financial Services", "Banks - Regional")[0] == NOT_HALAL
    assert business_screen("XYZ", "Technology", "Software - Application") == (HALAL, None)
    assert business_screen("XYZ", None, None)[0] == CHECK
    assert check("XYZ", None).status == CHECK


def test_halal_stock_passes_both_checks():
    result = check("ASML.AS", funda("ASML.AS", 0.2))
    assert result.status == HALAL and result.reasons == [] and result.icon == "✅"


def test_fx_conversion():
    assert to_eur(110.0, "USD", DEMO_RATES) == pytest.approx(100.0)
    assert to_eur(8500.0, "GBp", {"GBP": 0.85}) == pytest.approx(100.0)  # pence -> pounds -> euro
    assert to_eur(50.0, "EUR", {}) == 50.0
    assert to_eur(10.0, "HKD", {}) is None
    assert to_eur(None, "USD", DEMO_RATES) is None
    assert fx_tickers({"USD", "GBp", "EUR", "HKD"}) == {"USD": "EURUSD=X", "GBP": "EURGBP=X", "HKD": "EURHKD=X"}


def test_markets_and_flags():
    assert set(UNIVERSES) == {"Beliebt", "USA", "Europa", "China", "Alle Märkte"}
    assert len(UNIVERSES["Alle Märkte"]["tickers"]) == len(CATALOG) > 300
    assert all(market_of(t) == "CN" for t in CHINA)
    assert flag("SAP.DE") == "🇩🇪" and flag("0700.HK") == "🇨🇳" and flag("NIO") == "🇨🇳" and flag("AAPL") == "🇺🇸"
    assert market_of("NEW.PA") == "EU" and market_of("NEW.HK") == "CN" and market_of("NEW") == "US"


def test_quiz_is_deterministic_and_answerable():
    a, b = quiz(42), quiz(42)
    assert a == b and len(a) == 5
    for q in a:
        assert q.options[q.answer] == TERMS[q.key].short
        assert len(set(q.options)) == 3
    assert quiz(43) != a
    assert word_of_the_day() in TERMS and set(POOL) <= set(TERMS)
