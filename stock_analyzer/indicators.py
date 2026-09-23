"""Technical indicators computed on daily OHLCV data.

All functions take pandas Series indexed by date and return Series of the same
length (leading values are NaN until enough history is available).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=window).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index with Wilder smoothing (0..100)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    alpha = 1.0 / window
    avg_gain = gain.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=alpha, adjust=False, min_periods=window).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    # No losses at all in the window -> maximally overbought.
    out = out.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    # A completely flat window is neutral.
    out = out.where(~((avg_loss == 0) & (avg_gain == 0)), 50.0)
    return out


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False, min_periods=signal).mean()
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def atr(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
    """Average True Range with Wilder smoothing."""
    prev_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return true_range.ewm(alpha=1.0 / window, adjust=False, min_periods=window).mean()


def bollinger(close: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    mid = sma(close, window)
    std = close.rolling(window, min_periods=window).std()
    return pd.DataFrame({"mid": mid, "upper": mid + num_std * std, "lower": mid - num_std * std})


def rate_of_change(close: pd.Series, window: int) -> pd.Series:
    return close / close.shift(window) - 1.0


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff()).fillna(0.0)
    return (direction * volume.fillna(0.0)).cumsum()


def log_trend(close: pd.Series, window: int) -> tuple[float, float]:
    """Slope (per day) and R^2 of a linear fit on log prices over the last `window` days."""
    y = np.log(close.dropna().iloc[-window:].to_numpy(dtype=float))
    if len(y) < max(10, window // 3):
        return 0.0, 0.0
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    ss_res = float(np.sum((y - fitted) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return float(slope), float(r2)
