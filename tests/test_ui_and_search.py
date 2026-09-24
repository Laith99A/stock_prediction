import re
from pathlib import Path

import numpy as np
import pytest

from stock_analyzer import ui
from stock_analyzer.formatting import fmt_score
from stock_analyzer.glossary import CATEGORIES, TERMS
from stock_analyzer.recommendation import analyze
from stock_analyzer.scoring import LABELS, classify
from stock_analyzer.universes import CATALOG, UNIVERSES, search_catalog

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("query", "ticker"),
    [("Alphabet", "GOOGL"), ("google", "GOOGL"), ("GOOGL", "GOOGL"), ("sap", "SAP.DE"), ("münchener", "MUV2.DE"),
     ("munchener", "MUV2.DE"), ("VW", "VOW3.DE"), ("coca", "KO"), ("facebook", "META"), ("rheinmetall", "RHM.DE")],
)
def test_search_catalog_finds_by_name_ticker_and_alias(query, ticker):
    assert search_catalog(query)[0][0] == ticker


def test_search_catalog_no_match():
    assert search_catalog("xyz-unknown") == []
    assert search_catalog("  ") == []


def test_catalog_covers_all_lists():
    assert len(CATALOG) > 250
    for universe in UNIVERSES.values():
        assert set(universe["tickers"]) <= set(CATALOG)


def test_every_referenced_glossary_term_exists():
    sources = (ROOT / "app.py").read_text() + (ROOT / "stock_analyzer" / "ui.py").read_text()
    keys = set(re.findall(r"""(?:tip|info)\("(\w+)"\)""", sources))
    keys |= set(re.findall(r"""term\([^()]*?,\s*["'](\w+)["']\)""", sources))
    keys |= set(re.findall(r"""TERMS\['(\w+)'\]""", sources))
    assert keys, "no glossary references found"
    assert keys <= set(TERMS), keys - set(TERMS)
    assert {t.category for t in TERMS.values()} <= set(CATEGORIES)


def test_displayed_score_matches_category():
    for value in np.linspace(-100, 100, 4001):
        assert classify(int(fmt_score(value))) == classify(value), value


def test_html_components_render_for_every_side(uptrend, downtrend, sideways):
    from stock_analyzer.fundamentals import Fundamentals
    from stock_analyzer.halal import check

    for df in (uptrend, downtrend, sideways):
        rec = analyze(df, "T", name="Test <AG>")
        halal = check("AAPL", Fundamentals("AAPL", debt_to_equity=0.2))
        tile = ui.stock_tile(rec, halal, "🇺🇸", 100.0, 0.01, "Technologie", df["Close"])
        for markup in (tile, ui.detail_header(rec, 0.01, halal, "🇺🇸", 90.0), ui.action_box(rec),
                       ui.reasons_list(rec.reasons), ui.halal_card(halal)):
            assert markup.count("<div") == markup.count("</div>")
        assert "Test &lt;AG&gt;" in tile  # names are escaped
        assert "<svg" in tile and "100,00 €" in tile
    for label in LABELS:
        assert ui.badge(label).startswith('<span class="badge')
    assert ui.sparkline(uptrend["Close"]).count("#34d399") == 2  # rising line is green
    assert ui.sparkline(uptrend["Close"].iloc[:1]) == ""
