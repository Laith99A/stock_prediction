import numpy as np
import pandas as pd
import pytest

from stock_analyzer import charts
from stock_analyzer.chart_reader import DOWN, UP, crossings, pivots, read_chart, trend_structure
from stock_analyzer.chart_school import LESSONS, SHORT, example
from stock_analyzer.fundamentals import (
    BAD,
    GOOD,
    GROUPS,
    INFO,
    OK,
    Fundamentals,
    parse_info,
    rate,
    summarize,
    synthetic_fundamentals,
)
from stock_analyzer.glossary import TERMS

YAHOO_INFO = {
    "longName": "Example Inc.", "currency": "USD", "sector": "Technology", "currentPrice": 200.0,
    "marketCap": 3.0e12, "trailingPE": 32.0, "forwardPE": 28.0, "trailingPegRatio": 2.1, "priceToBook": 45.0,
    "priceToSalesTrailing12Months": 8.0, "enterpriseToEbitda": 24.0, "debtToEquity": 150.0, "currentRatio": 0.9,
    "returnOnEquity": 1.4, "profitMargins": 0.25, "revenueGrowth": 0.06, "earningsGrowth": 0.12,
    "dividendRate": 1.0, "dividendYield": 0.5, "payoutRatio": 0.15, "beta": 1.25, "trailingEps": 6.25,
    "targetMeanPrice": 230.0, "recommendationKey": "buy", "numberOfAnalystOpinions": 40,
}


def by_key(metrics):
    return {m.key: m for m in metrics}


def test_parse_info_converts_units():
    f = parse_info("EX", YAHOO_INFO)
    assert f.debt_to_equity == pytest.approx(1.5)  # Yahoo reports 150 (%)
    assert f.dividend_yield == pytest.approx(0.005)  # 1.00 $ / 200 $
    assert f.pe == 32.0 and f.pb == 45.0 and f.peg == 2.1
    assert f.analysts == 40 and f.available


def test_parse_info_fallbacks():
    no_dividend = parse_info("X", {"currentPrice": 10.0, "trailingPE": 12.0})
    assert no_dividend.dividend_yield == 0.0
    derived = parse_info("X", {"totalDebt": 500.0, "bookValue": 10.0, "sharesOutstanding": 100.0})
    assert derived.debt_to_equity == pytest.approx(0.5)
    empty = parse_info("X", {})
    assert not empty.available and empty.debt_to_equity is None and empty.dividend_yield is None
    assert parse_info("X", {"trailingPE": float("nan"), "priceToBook": "n/a"}).pe is None


@pytest.mark.parametrize(("de", "status"), [(0.3, GOOD), (0.9, GOOD), (1.5, OK), (2.5, BAD), (-0.4, BAD)])
def test_debt_to_equity_rating(de, status):
    metric = by_key(rate(Fundamentals("X", debt_to_equity=de)))["verschuldungsgrad"]
    assert metric.status == status and metric.highlight


def test_banks_get_no_debt_rating():
    metric = by_key(rate(Fundamentals("BANK", sector="Financial Services", debt_to_equity=8.0)))["verschuldungsgrad"]
    assert metric.status == INFO


def test_valuation_ratings():
    m = by_key(rate(parse_info("EX", YAHOO_INFO)))
    assert m["kgv"].status == BAD and m["kgv"].verdict == "teuer"
    assert by_key(rate(Fundamentals("X", pe=12.0)))["kgv"].status == GOOD
    assert by_key(rate(Fundamentals("X", pb=0.8)))["kbv"].verdict == "unter Buchwert"
    assert by_key(rate(Fundamentals("X", eps=-2.0)))["kgv"].verdict == "Verlust – kein KGV"


def test_summaries_and_glossary_coverage():
    metrics = rate(parse_info("EX", YAHOO_INFO))
    summaries = summarize(metrics)
    assert [s.group for s in summaries] == GROUPS
    assert {m.key for m in metrics} <= set(TERMS)
    dividend = next(s for s in summaries if "Dividende" in s.group)
    assert dividend.verdict == "Dividende niedrig"  # 0.5 % must not be called attractive


def test_synthetic_fundamentals_are_reproducible():
    a, b = synthetic_fundamentals("SAP.DE", 100.0), synthetic_fundamentals("SAP.DE", 100.0)
    assert a == b and a.is_demo and a.available


def _series(values):
    return pd.Series(values, index=pd.bdate_range("2025-01-01", periods=len(values)), dtype=float)


def test_trend_structure():
    t = np.arange(240)
    assert trend_structure(_series(100 + 0.3 * t + 3 * np.sin(t / 5))) == "Aufwärtstrend"
    assert trend_structure(_series(200 - 0.3 * t + 3 * np.sin(t / 5))) == "Abwärtstrend"
    assert trend_structure(_series(100 + 5 * np.sin(t / 5))) == "Seitwärtstrend"


def test_crossings_and_pivots():
    a, b = _series([1, 2, 3, 4, 5]), _series([3, 3, 3, 3, 3])
    assert [d for _, d in crossings(a, b)] == [1]
    highs = pivots(_series([1, 2, 5, 2, 1, 2, 3, 2, 1]), k=2, kind="high")
    assert list(highs) == [5.0, 3.0]  # both are the highest point within ±2 days


def test_read_chart_directions(uptrend, downtrend):
    up, down = read_chart(uptrend), read_chart(downtrend)
    assert up.direction == UP and up.trend == "Aufwärtstrend" and up.bullish > up.bearish
    assert down.direction == DOWN and down.trend == "Abwärtstrend"
    assert all(s.lesson in SHORT for s in up.signs + down.signs)


def test_lessons_and_charts_render(uptrend):
    pal = charts.PALETTES["light"]
    for lesson in LESSONS:
        fig = charts.lesson_chart(lesson.key, pal)
        assert (fig is None) == (not example(lesson.key))
    reading = read_chart(uptrend)
    assert len(charts.reading_chart(uptrend, reading, pal).data) >= 3
    fig = charts.indicator_chart(uptrend, pal)
    assert len(fig.layout.shapes) == 4  # RSI zones and 30/70 lines are drawn
