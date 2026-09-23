"""Turns scores into a concrete recommendation.

* BUY  → take-profit target, stop-loss and the date from which selling is
         recommended (time exit), plus the price below which the buy signal ends.
* HOLD → approximate date until which to hold (next re-evaluation) and the
         price levels that would turn the signal into BUY or SELL.
* SELL → the price level at which the sell signal would end.

Durations are estimated from two sources and averaged:
1. how long signals of the same kind lasted in this stock's own history
   (median remaining duration of past signals that were at least as old), and
2. the recent trend of the signal score, extrapolated to the next threshold.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import indicators as ind
from .formatting import LABEL_DE, fmt_num, fmt_pct
from .scoring import (
    BUY,
    BUY_THRESHOLD,
    HOLD,
    SELL,
    SELL_THRESHOLD,
    WEIGHTS,
    compute_scores,
    price_for_threshold,
)

# Horizon limits in trading days (≈ 21 per month).
HORIZON_LIMITS = {BUY: (10, 189), HOLD: (5, 126), SELL: (5, 126)}
HORIZON_DEFAULT = {BUY: 42, HOLD: 21, SELL: 21}

STOP_ATR = 2.0          # stop-loss distance in ATRs
MIN_TARGET_ATR = 3.0    # take-profit at least 3 ATRs away (reward/risk ≥ 1.5)
DRIFT_SHRINK = 0.5      # only trust half of the recent trend going forward
MAX_ANNUAL_DRIFT = math.log(1.6)

MIN_HISTORY = 130
# Score change per day below which the score trend is too flat to extrapolate.
MIN_SLOPE = 0.3


@dataclass
class Recommendation:
    ticker: str
    name: str
    currency: str
    as_of: pd.Timestamp
    price: float
    label: str
    score: float
    raw_score: float
    components: dict[str, float]
    strength: float
    signal_age: int
    horizon_days: int
    horizon_date: pd.Timestamp
    horizon_basis: str
    tendency: str
    atr: float
    annual_drift: float
    volatility: float
    target_price: float | None = None
    stop_loss: float | None = None
    upper_trigger: float | None = None
    lower_trigger: float | None = None
    reasons: list[tuple[str, int]] = field(default_factory=list)

    @property
    def label_de(self) -> str:
        return LABEL_DE[self.label]

    @property
    def expected_return(self) -> float | None:
        if self.target_price is None:
            return None
        return self.target_price / self.price - 1.0


class InsufficientDataError(ValueError):
    pass


def _runs(labels: pd.Series) -> list[tuple[str, int]]:
    """Consecutive runs of equal labels as (label, length)."""
    runs: list[tuple[str, int]] = []
    for label in labels:
        if runs and runs[-1][0] == label:
            runs[-1] = (label, runs[-1][1] + 1)
        else:
            runs.append((label, 1))
    return runs


def empirical_remaining(labels: pd.Series, min_samples: int = 3) -> tuple[float | None, int]:
    """Median remaining duration of past signals like the current one.

    Only completed signals are used (the first run is cut off by the start of the
    data and the last one is still running). Of those, only the ones that lasted
    longer than the current signal has already been active count.
    """
    runs = _runs(labels)
    if len(runs) < 2:
        return None, 0
    current, age = runs[-1]
    remaining = [length - age for label, length in runs[1:-1] if label == current and length > age]
    if len(remaining) < min_samples:
        return None, len(remaining)
    return float(np.median(remaining)), len(remaining)


def score_slope(signal: pd.Series, lookback: int = 10) -> float:
    y = signal.dropna().iloc[-lookback:].to_numpy(dtype=float)
    if len(y) < 3:
        return 0.0
    return float(np.polyfit(np.arange(len(y)), y, 1)[0])


def days_to_threshold(score: float, slope: float, threshold: float) -> float | None:
    gap = threshold - score
    if slope == 0 or np.sign(gap) != np.sign(slope):
        return None
    return gap / slope


def _next_threshold(label: str, slope: float) -> float:
    if label == BUY:
        return BUY_THRESHOLD
    if label == SELL:
        return SELL_THRESHOLD
    return BUY_THRESHOLD if slope > 0 else SELL_THRESHOLD


def estimate_horizon(label: str, labels: pd.Series, signal: pd.Series) -> tuple[int, str]:
    lo, hi = HORIZON_LIMITS[label]
    slope = score_slope(signal)
    estimates: list[float] = []
    basis: list[str] = []

    emp, n = empirical_remaining(labels)
    if emp is not None:
        estimates.append(min(max(emp, lo), hi))
        basis.append(f"historische Signaldauer dieser Aktie (n={n})")

    trend_days = None
    if abs(slope) >= MIN_SLOPE:
        trend_days = days_to_threshold(float(signal.dropna().iloc[-1]), slope, _next_threshold(label, slope))
    if trend_days is not None:
        estimates.append(min(max(trend_days, lo), hi))
        basis.append("Trend des Scores")

    if not estimates:
        return HORIZON_DEFAULT[label], "Standardwert (zu wenig Historie)"
    days = int(round(min(max(float(np.mean(estimates)), lo), hi)))
    return days, " + ".join(basis)


def signal_strength(label: str, score: float, components: dict[str, float]) -> float:
    """0..1: distance beyond the threshold combined with how many factors agree."""
    total = sum(WEIGHTS[k] for k, v in components.items() if np.isfinite(v))
    if total == 0:
        return 0.0
    if label == BUY:
        margin = (score - BUY_THRESHOLD) / 25.0
        agree = sum(WEIGHTS[k] for k, v in components.items() if np.isfinite(v) and v > 0.1)
    elif label == SELL:
        margin = (SELL_THRESHOLD - score) / 25.0
        agree = sum(WEIGHTS[k] for k, v in components.items() if np.isfinite(v) and v < -0.1)
    else:
        margin = min(score - SELL_THRESHOLD, BUY_THRESHOLD - score) / 25.0
        agree = sum(WEIGHTS[k] for k, v in components.items() if np.isfinite(v) and abs(v) <= 0.4)
    return float(0.5 * min(max(margin, 0.0), 1.0) + 0.5 * agree / total)


def _tendency(slope: float) -> str:
    if slope >= MIN_SLOPE:
        return "steigend"
    if slope <= -MIN_SLOPE:
        return "fallend"
    return "seitwärts"


def _reasons(df: pd.DataFrame, comps: dict[str, float], benchmark: pd.Series | None) -> list[tuple[str, int]]:
    close = df["Close"]
    price = float(close.iloc[-1])
    out: list[tuple[str, int]] = []

    sma200 = ind.sma(close, 200).iloc[-1]
    sma50 = ind.sma(close, 50).iloc[-1]
    if np.isfinite(sma200):
        diff = price / sma200 - 1
        where = "über" if diff >= 0 else "unter"
        out.append((f"Kurs liegt {fmt_pct(abs(diff), sign=False)} {where} der 200-Tage-Linie", 1 if diff >= 0 else -1))
        if sma50 >= sma200:
            out.append(("Golden Cross: 50-Tage-Linie über 200-Tage-Linie", 1))
        else:
            out.append(("Death Cross: 50-Tage-Linie unter 200-Tage-Linie", -1))
    elif np.isfinite(sma50):
        diff = price / sma50 - 1
        where = "über" if diff >= 0 else "unter"
        out.append((f"Kurs liegt {fmt_pct(abs(diff), sign=False)} {where} der 50-Tage-Linie", 1 if diff >= 0 else -1))

    for window, text in ((126, "6-Monats-Performance"), (63, "3-Monats-Performance")):
        roc = ind.rate_of_change(close, window).iloc[-1]
        if np.isfinite(roc):
            out.append((f"{text}: {fmt_pct(roc)}", int(np.sign(roc))))
            break

    hist = ind.macd(close)["hist"].iloc[-1]
    if np.isfinite(hist):
        if hist >= 0:
            out.append(("MACD über der Signallinie (positives Momentum)", 1))
        else:
            out.append(("MACD unter der Signallinie (nachlassendes Momentum)", -1))

    rsi = ind.rsi(close).iloc[-1]
    if np.isfinite(rsi):
        if rsi >= 75:
            out.append((f"RSI {fmt_num(rsi, 0)} – überkauft, Rücksetzergefahr", -1))
        elif rsi >= 65:
            out.append((f"RSI {fmt_num(rsi, 0)} – starke Nachfrage, nahe am überkauften Bereich", 0))
        elif rsi <= 30:
            out.append((f"RSI {fmt_num(rsi, 0)} – überverkauft, Erholungspotenzial", 1))
        else:
            out.append((f"RSI {fmt_num(rsi, 0)} – neutraler Bereich", 0))

    high = close.iloc[-252:].max()
    dd = price / high - 1
    if dd > -0.1:
        out.append((f"Nahe am 52-Wochen-Hoch ({fmt_pct(dd)})", 1))
    elif dd < -0.25:
        out.append((f"Weit unter dem 52-Wochen-Hoch ({fmt_pct(dd)})", -1))

    vol = comps.get("volume", np.nan)
    if np.isfinite(vol) and vol > 0.3:
        out.append(("Volumen bestätigt die Aufwärtsbewegung", 1))
    elif np.isfinite(vol) and vol < -0.3:
        out.append(("Abgabedruck: Umsatz an Verlusttagen überwiegt", -1))

    if benchmark is not None and not benchmark.dropna().empty:
        bench = benchmark.reindex(close.index).ffill()
        rel = ind.rate_of_change(close, 63).iloc[-1] - ind.rate_of_change(bench, 63).iloc[-1]
        if np.isfinite(rel):
            points = f"{'+' if rel >= 0 else '−'}{fmt_num(abs(rel) * 100, 1)} Prozentpunkte"
            if rel >= 0:
                out.append((f"Stärker als der Markt (3 Monate: {points})", 1))
            else:
                out.append((f"Schwächer als der Markt (3 Monate: {points})", -1))
        market = comps.get("market", np.nan)
        if np.isfinite(market):
            if market > 0.3:
                out.append(("Marktumfeld positiv (Index im Aufwärtstrend)", 1))
            elif market < -0.3:
                out.append(("Marktumfeld negativ (Index im Abwärtstrend)", -1))
            else:
                out.append(("Marktumfeld neutral", 0))
    return out


def analyze(
    df: pd.DataFrame,
    ticker: str,
    name: str | None = None,
    currency: str = "",
    benchmark: pd.Series | None = None,
    with_triggers: bool = True,
    scores: pd.DataFrame | None = None,
) -> Recommendation:
    """Analyse one stock's daily OHLCV history and return a recommendation."""
    if df is None or len(df) < MIN_HISTORY:
        raise InsufficientDataError(
            f"{ticker}: mindestens {MIN_HISTORY} Handelstage Historie nötig, vorhanden: {0 if df is None else len(df)}"
        )
    if scores is None:
        scores = compute_scores(df, benchmark)
    valid = scores.dropna(subset=["signal"])
    if valid.empty:
        raise InsufficientDataError(f"{ticker}: Score konnte nicht berechnet werden")

    last = valid.iloc[-1]
    label = str(last["label"])
    score = float(last["signal"])
    components = {k: float(last[k]) for k in WEIGHTS}
    labels = valid["label"]
    signal_age = _runs(labels)[-1][1]

    close = df["Close"]
    price = float(close.iloc[-1])
    as_of = pd.Timestamp(df.index[-1])
    atr = float(ind.atr(df["High"], df["Low"], close).iloc[-1])
    if not np.isfinite(atr) or atr <= 0:
        atr = price * 0.02
    daily_drift, _ = ind.log_trend(close, 126)
    log_returns = np.log(close).diff()
    volatility = float(log_returns.iloc[-60:].std() * np.sqrt(252))

    horizon_days, horizon_basis = estimate_horizon(label, labels, valid["signal"])
    horizon_date = as_of + pd.offsets.BDay(horizon_days)
    slope = score_slope(valid["signal"])

    rec = Recommendation(
        ticker=ticker,
        name=name or ticker,
        currency=currency,
        as_of=as_of,
        price=price,
        label=label,
        score=score,
        raw_score=float(last["raw"]),
        components=components,
        strength=signal_strength(label, score, components),
        signal_age=signal_age,
        horizon_days=horizon_days,
        horizon_date=horizon_date,
        horizon_basis=horizon_basis,
        tendency=_tendency(slope),
        atr=atr,
        annual_drift=daily_drift * 252,
        volatility=volatility,
        reasons=_reasons(df, components, benchmark),
    )

    if label == BUY:
        drift = min(max(daily_drift, 0.0) * DRIFT_SHRINK, MAX_ANNUAL_DRIFT / 252)
        rec.target_price = max(price * math.exp(drift * horizon_days), price + MIN_TARGET_ATR * atr)
        rec.stop_loss = max(price - STOP_ATR * atr, 0.01 * price)

    if with_triggers:
        step = 0.5 * atr
        if label in (BUY, HOLD):
            rec.lower_trigger = price_for_threshold(
                df, benchmark, BUY_THRESHOLD if label == BUY else SELL_THRESHOLD, "down", step
            )
        if label in (HOLD, SELL):
            rec.upper_trigger = price_for_threshold(
                df, benchmark, BUY_THRESHOLD if label == HOLD else SELL_THRESHOLD, "up", step
            )
    return rec
