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
    for df in (uptrend, downtrend, sideways):
        rec = analyze(df, "T", name="Test <AG>")
        for markup in (ui.stock_card(rec), ui.detail_header(rec, 0.01), ui.action_box(rec), ui.reasons_list(rec.reasons)):
            assert markup.count("<div") == markup.count("</div>")
        assert "Test &lt;AG&gt;" in ui.stock_card(rec)  # names are escaped
    for label in LABELS:
        assert ui.badge(label).startswith('<span class="badge')
    assert "dist" in ui.distribution_bar({label: 1 for label in LABELS})
