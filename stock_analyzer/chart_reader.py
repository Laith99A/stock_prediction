"""Reads the current chart like a chart analyst would and lists the signs that
typically point to rising or falling prices.

No single sign is reliable on its own; the reading counts how many point in each
direction.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import indicators as ind
from .formatting import fmt_date, fmt_num, fmt_pct

UP, DOWN, NEUTRAL = 1, -1, 0


@dataclass
class Sign:
    text: str
    direction: int
    lesson: str  # chart school lesson that explains this sign
    date: pd.Timestamp | None = None
    price: float | None = None  # where to mark it on the chart


@dataclass
class ChartReading:
    signs: list[Sign]
    trend: str
    support: float | None
    resistance: float | None
    crosses: list[tuple[pd.Timestamp, float, str]] = field(default_factory=list)  # (date, price, kind)

    @property
    def bullish(self) -> int:
        return sum(s.direction == UP for s in self.signs)

    @property
    def bearish(self) -> int:
        return sum(s.direction == DOWN for s in self.signs)

    @property
    def verdict(self) -> str:
        diff = self.bullish - self.bearish
        if diff >= 3:
            return "Deutlich mehr Zeichen für steigende Kurse"
        if diff >= 1:
            return "Etwas mehr Zeichen für steigende Kurse"
        if diff <= -3:
            return "Deutlich mehr Zeichen für fallende Kurse"
        if diff <= -1:
            return "Etwas mehr Zeichen für fallende Kurse"
        return "Gemischtes Bild – die Zeichen heben sich auf"

    @property
    def direction(self) -> int:
        return int(np.sign(self.bullish - self.bearish))


def trend_structure(close: pd.Series, days: int = 120, parts: int = 4) -> str:
    """Compare highs and lows of consecutive periods: higher highs and higher lows = uptrend."""
    window = close.iloc[-days:]
    if len(window) < days // 2:
        return "Seitwärtstrend"
    chunks = np.array_split(window.to_numpy(), parts)
    highs = [c.max() for c in chunks]
    lows = [c.min() for c in chunks]
    rising = sum(b > a for a, b in zip(highs, highs[1:])) + sum(b > a for a, b in zip(lows, lows[1:]))
    steps = 2 * (parts - 1)
    if rising >= steps - 1:
        return "Aufwärtstrend"
    if rising <= 1:
        return "Abwärtstrend"
    return "Seitwärtstrend"


def pivots(series: pd.Series, k: int = 5, kind: str = "high") -> pd.Series:
    """Local extremes: a point that is the highest (lowest) of k days on both sides."""
    roll = series.rolling(2 * k + 1, center=True)
    extreme = roll.max() if kind == "high" else roll.min()
    return series[series == extreme].dropna()


def crossings(a: pd.Series, b: pd.Series) -> list[tuple[pd.Timestamp, int]]:
    """Dates where a crosses b: +1 = from below to above, -1 = from above to below."""
    # A day where both lines are exactly equal is not a crossing by itself.
    diff = np.sign((a - b).dropna()).replace(0, np.nan).ffill().dropna()
    change = diff.diff()
    return [(date, int(np.sign(v))) for date, v in change[change != 0].dropna().items()]


def read_chart(df: pd.DataFrame, lookback: int = 180) -> ChartReading:
    close = df["Close"]
    price = float(close.iloc[-1])
    today = close.index[-1]
    signs: list[Sign] = []

    # 1) trend structure
    trend = trend_structure(close)
    if trend == "Aufwärtstrend":
        signs.append(Sign("Höhere Hochs und höhere Tiefs in den letzten 6 Monaten – ein Aufwärtstrend", UP, "trend"))
    elif trend == "Abwärtstrend":
        signs.append(Sign("Tiefere Hochs und tiefere Tiefs in den letzten 6 Monaten – ein Abwärtstrend", DOWN, "trend"))
    else:
        signs.append(Sign("Weder klar höhere noch tiefere Hochs – die Aktie läuft seitwärts", NEUTRAL, "trend"))

    # 2) moving averages
    sma50, sma200 = ind.sma(close, 50), ind.sma(close, 200)
    if np.isfinite(sma200.iloc[-1]):
        above = price > sma200.iloc[-1]
        signs.append(Sign(
            f"Kurs {'über' if above else 'unter'} der 200-Tage-Linie ({fmt_pct(price / sma200.iloc[-1] - 1)}) – "
            f"langfristiger Trend {'intakt' if above else 'angeschlagen'}", UP if above else DOWN, "durchschnitte"))
    crosses = []
    for date, direction in crossings(sma50, sma200):
        crosses.append((date, float(close.loc[date]), "Golden Cross" if direction > 0 else "Death Cross"))
    recent = [c for c in crosses if (today - c[0]).days <= 180]
    if recent:
        date, cross_price, kind = recent[-1]
        golden = kind == "Golden Cross"
        signs.append(Sign(f"{kind} am {fmt_date(date)}: 50-Tage-Linie kreuzt die 200-Tage-Linie nach "
                          f"{'oben' if golden else 'unten'}", UP if golden else DOWN, "durchschnitte", date, cross_price))
    for date, direction in crossings(close, sma50)[-1:]:
        if len(close.loc[date:]) <= 10:
            signs.append(Sign(f"Kurs hat am {fmt_date(date)} die 50-Tage-Linie nach {'oben' if direction > 0 else 'unten'} "
                              f"durchbrochen", UP if direction > 0 else DOWN, "durchschnitte", date, float(close.loc[date])))

    # 3) breakout to a new 3-month high / low
    prior = close.iloc[-68:-3]
    breakout = breakdown = False
    if len(prior) > 20:
        breakout = close.iloc[-3:].max() > prior.max() and price >= prior.max()
        breakdown = close.iloc[-3:].min() < prior.min() and price <= prior.min()
    if breakout:
        signs.append(Sign("Ausbruch: Kurs auf dem höchsten Stand seit 3 Monaten", UP, "unterstuetzung", today, price))
    elif breakdown:
        signs.append(Sign("Bruch nach unten: Kurs auf dem tiefsten Stand seit 3 Monaten", DOWN, "unterstuetzung",
                          today, price))

    # 4) support and resistance from recent turning points
    window = df.iloc[-lookback:]
    k = 5
    confirmed = window.iloc[:-k] if len(window) > 2 * k else window
    highs = pivots(confirmed["High"], k, "high")
    lows = pivots(confirmed["Low"], k, "low")
    above = highs[highs > price * 1.005]
    below = lows[lows < price * 0.995]
    resistance = float(above.min()) if len(above) else None
    support = float(below.max()) if len(below) else None
    if resistance is None and not breakout:
        signs.append(Sign("Kurs liegt über allen Hochs der letzten Monate – kein Widerstand in Sicht", UP, "unterstuetzung"))
    elif resistance is not None and resistance / price - 1 < 0.02:
        signs.append(Sign(f"Kurs läuft auf einen Widerstand bei {fmt_num(resistance)} zu – dort drehte er zuletzt nach unten",
                          NEUTRAL, "unterstuetzung"))
    if support is None and not breakdown:
        signs.append(Sign("Kurs liegt unter allen Tiefs der letzten Monate – keine Unterstützung in Sicht", DOWN,
                          "unterstuetzung"))
    elif support is not None and 1 - support / price < 0.02:
        signs.append(Sign(f"Kurs nahe der Unterstützung bei {fmt_num(support)} – dort drehte er zuletzt nach oben",
                          NEUTRAL, "unterstuetzung"))

    # 5) volume
    if df["Volume"].iloc[-20:].sum() > 0:
        change = close.diff().iloc[-20:]
        vol = df["Volume"].iloc[-20:]
        up_vol, down_vol = vol[change > 0].sum(), vol[change < 0].sum()
        if down_vol > 0 and up_vol / down_vol > 1.3:
            signs.append(Sign("An Tagen mit Kursgewinnen wird deutlich mehr gehandelt – Käufer sind aktiv", UP, "volumen"))
        elif up_vol > 0 and down_vol / up_vol > 1.3:
            signs.append(Sign("An Tagen mit Kursverlusten wird deutlich mehr gehandelt – Verkaufsdruck", DOWN, "volumen"))

    # 6) RSI
    rsi = float(ind.rsi(close).iloc[-1])
    if rsi >= 70:
        signs.append(Sign(f"RSI {fmt_num(rsi, 0)}: überkauft – nach starkem Anstieg ist eine Pause wahrscheinlicher",
                          DOWN, "rsi"))
    elif rsi <= 30:
        signs.append(Sign(f"RSI {fmt_num(rsi, 0)}: überverkauft – nach starkem Fall ist eine Erholung möglich", UP, "rsi"))
    else:
        signs.append(Sign(f"RSI {fmt_num(rsi, 0)}: weder überkauft noch überverkauft", NEUTRAL, "rsi"))

    # 7) MACD crossing
    macd = ind.macd(close)
    macd_cross = crossings(macd["macd"], macd["signal"])
    if macd_cross and len(close.loc[macd_cross[-1][0]:]) <= 10:
        date, direction = macd_cross[-1]
        signs.append(Sign(f"MACD hat am {fmt_date(date)} die Signallinie nach {'oben' if direction > 0 else 'unten'} "
                          f"gekreuzt – Schwung {'nimmt zu' if direction > 0 else 'lässt nach'}",
                          UP if direction > 0 else DOWN, "macd", date, float(close.loc[date])))
    elif np.isfinite(macd["hist"].iloc[-1]):
        rising = macd["hist"].iloc[-1] > 0
        signs.append(Sign(f"MACD liegt {'über' if rising else 'unter'} der Signallinie", UP if rising else DOWN, "macd"))

    return ChartReading(signs=signs, trend=trend, support=support, resistance=resistance, crosses=crosses)
