import numpy as np
import pandas as pd

from stock_analyzer import indicators as ind


def test_sma_matches_manual_mean():
    s = pd.Series(np.arange(1.0, 11.0))
    out = ind.sma(s, 3)
    assert out.iloc[:2].isna().all()
    assert out.iloc[-1] == (8 + 9 + 10) / 3


def test_rsi_extremes():
    rising = pd.Series(np.arange(1.0, 60.0))
    falling = rising[::-1].reset_index(drop=True)
    flat = pd.Series(np.full(60, 5.0))
    assert ind.rsi(rising).iloc[-1] == 100.0
    assert ind.rsi(falling).iloc[-1] < 1.0
    assert ind.rsi(flat).iloc[-1] == 50.0


def test_atr_constant_range():
    close = pd.Series(np.full(50, 100.0))
    atr = ind.atr(close + 1, close - 1, close)
    assert abs(atr.iloc[-1] - 2.0) < 1e-9


def test_log_trend_recovers_growth_rate():
    close = pd.Series(100 * np.exp(0.002 * np.arange(200)))
    slope, r2 = ind.log_trend(close, 126)
    assert abs(slope - 0.002) < 1e-9
    assert r2 > 0.999


def test_macd_positive_in_uptrend():
    close = pd.Series(100 * np.exp(0.003 * np.arange(100)))
    assert ind.macd(close)["macd"].iloc[-1] > 0
