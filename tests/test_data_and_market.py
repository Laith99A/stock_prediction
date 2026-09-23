import numpy as np
import pandas as pd

from stock_analyzer.backtest import signal_quality, strategy_performance
from stock_analyzer.data import SyntheticProvider, clean_ohlcv, guess_currency, split_download
from stock_analyzer.formatting import fmt_date, fmt_pct, fmt_price
from stock_analyzer.market import scan
from stock_analyzer.scoring import compute_scores


def _frame(n=5, tz=None):
    idx = pd.date_range("2026-01-01", periods=n, freq="B", tz=tz)
    return pd.DataFrame(
        {"Open": 1.0, "High": 2.0, "Low": 0.5, "Close": np.arange(1.0, n + 1), "Volume": 10.0}, index=idx
    )


def test_split_download_handles_both_layouts():
    a, b = _frame(), _frame() * 2
    by_ticker = pd.concat({"AAA": a, "BBB": b}, axis=1)  # (Ticker, Price)
    by_price = by_ticker.swaplevel(0, 1, axis=1)  # (Price, Ticker)
    for raw in (by_ticker, by_price):
        out = split_download(raw, ["AAA", "BBB", "MISSING"])
        assert set(out) == {"AAA", "BBB"}
        assert out["BBB"]["Close"].iloc[-1] == 10.0
    assert list(split_download(_frame(), ["ONE"])) == ["ONE"]
    assert split_download(pd.DataFrame(), ["X"]) == {}


def test_clean_ohlcv_drops_nan_and_timezone():
    df = _frame(tz="Europe/Berlin")
    df.iloc[1, df.columns.get_loc("Close")] = np.nan
    out = clean_ohlcv(df)
    assert len(out) == 4
    assert out.index.tz is None


def test_guess_currency():
    assert guess_currency("SAP.DE") == "EUR"
    assert guess_currency("AAPL") == "USD"
    assert guess_currency("BRK-B") == "USD"
    assert guess_currency("NESN.SW") == "CHF"
    assert guess_currency("^GDAXI") == ""


def test_synthetic_provider_is_deterministic():
    p = SyntheticProvider(end="2026-09-23")
    a = p.history(["X"], "2y")["X"]
    b = p.history(["X"], "2y")["X"]
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 504
    assert (a["High"] >= a[["Open", "Close"]].max(axis=1)).all()
    assert (a["Low"] <= a[["Open", "Close"]].min(axis=1)).all()


def test_scan_with_demo_data():
    result = scan(SyntheticProvider(end="2026-09-23"), {"AAA": "A", "BBB": "B", "CCC": "C"}, "^IDX", "Index")
    assert len(result.recommendations) == 3
    assert result.regime is not None and result.regime.name == "Index"
    scores = [r.score for r in result.recommendations]
    assert scores == sorted(scores, reverse=True)
    table = result.table()
    assert {"Ticker", "Empfehlung", "Datum", "Kursziel", "Stop-Loss"} <= set(table.columns)


def test_backtest(uptrend):
    scores = compute_scores(uptrend)
    quality = signal_quality(scores, uptrend["Close"])
    assert quality.loc["ALL", "days"] > 0
    result = strategy_performance(scores, uptrend["Close"])
    assert result.equity["strategy"].iloc[0] == 1.0
    assert 0 < result.time_in_market <= 1


def test_backtest_always_invested_equals_buy_and_hold(uptrend):
    scores = pd.DataFrame({"label": "BUY"}, index=uptrend.index)
    result = strategy_performance(scores, uptrend["Close"])
    assert abs(result.strategy_return - result.buy_and_hold_return) < 1e-9


def test_german_formatting():
    assert fmt_price(1234.5, "EUR") == "1.234,50 €"
    assert fmt_pct(0.1234) == "+12,3 %"
    assert fmt_pct(-0.05, sign=False) == "-5,0 %"
    assert fmt_date(pd.Timestamp("2026-11-16")) == "16.11.2026"
    assert fmt_price(None) == "–"
