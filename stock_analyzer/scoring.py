"""Composite score (-100 … +100) and five-level classification
(Strong Buy / Buy / Hold / Sell / Strong Sell).

Every factor is mapped to the range [-1, 1] (positive = bullish). The raw score
is the weighted average of all available factors times 100. The signal score is
a short EMA of the raw score so that the classification does not flicker from
day to day.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import indicators as ind

STRONG_BUY = "STRONG_BUY"
BUY = "BUY"
HOLD = "HOLD"
SELL = "SELL"
STRONG_SELL = "STRONG_SELL"
LABELS = [STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL]

# The "side" groups the strong variants with their normal counterpart: a stock
# that goes from Strong Buy to Buy is still a buy and should not be sold.
SIDE = {STRONG_BUY: BUY, BUY: BUY, HOLD: HOLD, SELL: SELL, STRONG_SELL: SELL}

STRONG_BUY_THRESHOLD = 55.0
BUY_THRESHOLD = 25.0
SELL_THRESHOLD = -25.0
STRONG_SELL_THRESHOLD = -55.0
SMOOTHING_SPAN = 5

WEIGHTS: dict[str, float] = {
    "trend": 0.25,
    "momentum": 0.25,
    "rsi": 0.10,
    "high52": 0.10,
    "volume": 0.10,
    "relative": 0.10,
    "market": 0.10,
}

COMPONENT_LABELS: dict[str, str] = {
    "trend": "Trend (gleitende Durchschnitte)",
    "momentum": "Momentum (Performance, MACD)",
    "rsi": "RSI (überkauft/überverkauft)",
    "high52": "Abstand zum 52-Wochen-Hoch",
    "volume": "Volumen (On-Balance-Volume)",
    "relative": "Relative Stärke vs. Markt",
    "market": "Marktumfeld (Index-Trend)",
}

# Minimum share of the total weight that must be available for a valid score.
MIN_WEIGHT = 0.5


def _mean_available(parts: list[pd.Series]) -> pd.Series:
    return pd.concat(parts, axis=1).mean(axis=1, skipna=True)


def trend_component(close: pd.Series) -> pd.Series:
    sma50 = ind.sma(close, 50)
    sma200 = ind.sma(close, 200)
    parts = [
        np.tanh((close / sma200 - 1.0) / 0.08),
        np.tanh((sma50 / sma200 - 1.0) / 0.05),
        np.tanh((close / sma50 - 1.0) / 0.05),
        np.tanh((sma50 / sma50.shift(20) - 1.0) / 0.03),
    ]
    return _mean_available(parts)


def momentum_component(close: pd.Series, high: pd.Series, low: pd.Series) -> pd.Series:
    hist = ind.macd(close)["hist"]
    atr = ind.atr(high, low, close)
    parts = [
        np.tanh(ind.rate_of_change(close, 126) / 0.20),
        np.tanh(ind.rate_of_change(close, 63) / 0.12),
        np.tanh(hist / atr.replace(0.0, np.nan) / 0.25),
    ]
    return _mean_available(parts)


# RSI → score. Oversold gives a small rebound bonus, 55–70 is healthy strength,
# above ~75 the stock is overbought and the score turns negative.
_RSI_X = [0, 20, 30, 45, 55, 65, 72, 80, 100]
_RSI_Y = [0.4, 0.4, 0.1, -0.2, 0.3, 0.6, 0.3, -0.4, -1.0]


def rsi_component(close: pd.Series) -> pd.Series:
    r = ind.rsi(close)
    values = np.interp(r.fillna(50.0).to_numpy(), _RSI_X, _RSI_Y)
    return pd.Series(values, index=close.index).where(r.notna())


_DD_X = [-0.6, -0.35, -0.2, -0.1, -0.03, 0.0]
_DD_Y = [-1.0, -0.7, -0.3, 0.1, 0.5, 0.7]


def high52_component(close: pd.Series) -> pd.Series:
    high = close.rolling(252, min_periods=60).max()
    drawdown = close / high - 1.0
    values = np.interp(drawdown.fillna(0.0).to_numpy(), _DD_X, _DD_Y)
    return pd.Series(values, index=close.index).where(drawdown.notna())


def volume_component(close: pd.Series, volume: pd.Series, window: int = 20) -> pd.Series:
    signed = np.sign(close.diff()).fillna(0.0) * volume.fillna(0.0)
    total = volume.fillna(0.0).rolling(window, min_periods=window).sum()
    ratio = signed.rolling(window, min_periods=window).sum() / total.replace(0.0, np.nan)
    return np.tanh(ratio / 0.3)


def relative_component(close: pd.Series, benchmark: pd.Series | None) -> pd.Series:
    if benchmark is None or benchmark.dropna().empty:
        return pd.Series(np.nan, index=close.index)
    bench = benchmark.reindex(close.index).ffill()
    parts = [
        np.tanh((ind.rate_of_change(close, 63) - ind.rate_of_change(bench, 63)) / 0.10),
        np.tanh((ind.rate_of_change(close, 126) - ind.rate_of_change(bench, 126)) / 0.15),
    ]
    return _mean_available(parts)


def market_component(index: pd.Index, benchmark: pd.Series | None) -> pd.Series:
    if benchmark is None or benchmark.dropna().empty:
        return pd.Series(np.nan, index=index)
    return trend_component(benchmark.dropna()).reindex(index).ffill()


def classify(signal: float) -> str | None:
    if signal is None or not np.isfinite(signal):
        return None
    if signal >= STRONG_BUY_THRESHOLD:
        return STRONG_BUY
    if signal >= BUY_THRESHOLD:
        return BUY
    if signal <= STRONG_SELL_THRESHOLD:
        return STRONG_SELL
    if signal <= SELL_THRESHOLD:
        return SELL
    return HOLD


def compute_components(df: pd.DataFrame, benchmark: pd.Series | None = None) -> pd.DataFrame:
    close, high, low = df["Close"], df["High"], df["Low"]
    volume = df["Volume"] if "Volume" in df else pd.Series(0.0, index=df.index)
    return pd.DataFrame(
        {
            "trend": trend_component(close),
            "momentum": momentum_component(close, high, low),
            "rsi": rsi_component(close),
            "high52": high52_component(close),
            "volume": volume_component(close, volume),
            "relative": relative_component(close, benchmark),
            "market": market_component(df.index, benchmark),
        },
        index=df.index,
    )


def raw_score(components: pd.DataFrame) -> pd.Series:
    weights = pd.Series(WEIGHTS)
    comps = components[weights.index]
    available = comps.notna().mul(weights, axis=1).sum(axis=1)
    weighted = comps.fillna(0.0).mul(weights, axis=1).sum(axis=1)
    score = 100.0 * weighted / available.replace(0.0, np.nan)
    return score.where(available >= MIN_WEIGHT)


def compute_scores(df: pd.DataFrame, benchmark: pd.Series | None = None) -> pd.DataFrame:
    """Components, raw score, smoothed signal score and label for every day."""
    out = compute_components(df, benchmark)
    out["raw"] = raw_score(out)
    out["signal"] = out["raw"].ewm(span=SMOOTHING_SPAN, adjust=False, ignore_na=True).mean()
    out["signal"] = out["signal"].where(out["raw"].notna())
    out["label"] = [classify(v) for v in out["signal"]]
    out["side"] = out["label"].map(SIDE)
    return out


# ---------------------------------------------------------------------------
# Price triggers: "at which price would the signal flip?"
# ---------------------------------------------------------------------------

# Enough history for the 200-day average and the 52-week high.
_TRIGGER_WINDOW = 320
# Scenario length: the price moves to the candidate level over this many days.
TRIGGER_DAYS = 5


def extend_with_path(df: pd.DataFrame, target: float, days: int = TRIGGER_DAYS) -> pd.DataFrame:
    """Append `days` synthetic sessions in which the close moves linearly from
    the last close to `target` with average range and volume."""
    last_close = float(df["Close"].iloc[-1])
    closes = np.linspace(last_close, target, days + 1)[1:]
    opens = np.concatenate([[last_close], closes[:-1]])
    recent = df.iloc[-20:]
    half_range = float(((recent["High"] - recent["Low"]) / recent["Close"]).median()) / 2
    half_range = half_range if np.isfinite(half_range) else 0.01
    volume = float(recent["Volume"].mean()) if "Volume" in df else 0.0
    index = pd.bdate_range(df.index[-1] + pd.offsets.BDay(1), periods=days)
    path = pd.DataFrame(
        {
            "Open": opens,
            "High": np.maximum(opens, closes) * (1 + half_range),
            "Low": np.minimum(opens, closes) * (1 - half_range),
            "Close": closes,
            "Volume": volume,
        },
        index=index,
    )
    return pd.concat([df[path.columns], path])


def signal_after_path(df: pd.DataFrame, benchmark: pd.Series | None, target: float) -> float:
    """Signal score after the price moved to `target` within TRIGGER_DAYS days.

    The benchmark is assumed to stay flat during the scenario.
    """
    extended = extend_with_path(df, target)
    bench = None
    if benchmark is not None:
        bench = benchmark.reindex(benchmark.index.union(extended.index)).ffill()
    return float(compute_scores(extended, bench)["signal"].iloc[-1])


def price_for_threshold(
    df: pd.DataFrame,
    benchmark: pd.Series | None,
    threshold: float,
    direction: str,
    step: float,
    max_steps: int = 16,
) -> float | None:
    """Price level that, if reached within about a week, moves the signal
    score across `threshold`.

    direction="up": lowest price with signal >= threshold.
    direction="down": highest price with signal <= threshold.
    Returns the current close if that already happens with an unchanged price
    and None if the threshold is out of reach (more than `max_steps` * `step`).
    """
    if step <= 0 or not np.isfinite(step):
        return None
    base = df.iloc[-_TRIGGER_WINDOW:]
    bench = None
    if benchmark is not None:
        bench = benchmark.loc[: base.index[-1]].iloc[-_TRIGGER_WINDOW:]
    close = float(base["Close"].iloc[-1])
    sign = 1.0 if direction == "up" else -1.0

    def reached(price: float) -> bool:
        s = signal_after_path(base, bench, price)
        return s >= threshold if direction == "up" else s <= threshold

    if reached(close):
        return close
    prev = close
    for k in range(1, max_steps + 1):
        candidate = close + sign * k * step
        if candidate <= 0:
            return None
        if reached(candidate):
            lo, hi = prev, candidate  # lo: not reached, hi: reached
            for _ in range(6):
                mid = (lo + hi) / 2.0
                if reached(mid):
                    hi = mid
                else:
                    lo = mid
            return hi
        prev = candidate
    return None
