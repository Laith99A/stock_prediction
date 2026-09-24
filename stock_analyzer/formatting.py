"""German number, currency and date formatting."""
from __future__ import annotations

import math

import pandas as pd

LABEL_DE = {
    "STRONG_BUY": "Stark kaufen",
    "BUY": "Kaufen",
    "HOLD": "Halten",
    "SELL": "Verkaufen",
    "STRONG_SELL": "Stark verkaufen",
}
LABEL_ICON = {"STRONG_BUY": "🟢🟢", "BUY": "🟢", "HOLD": "🟡", "SELL": "🔴", "STRONG_SELL": "🔴🔴"}


def label_text(label: str) -> str:
    """Recommendation with traffic-light icon, e.g. "🟢🟢 Stark kaufen"."""
    return f"{LABEL_ICON[label]} {LABEL_DE[label]}"

_CURRENCY_SYMBOL = {"EUR": "€", "USD": "$", "GBp": "GBp", "CHF": "CHF", "JPY": "¥"}


def _de(number_text: str) -> str:
    return number_text.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_num(value: float | None, decimals: int = 2) -> str:
    if value is None or not math.isfinite(value):
        return "–"
    return _de(f"{value:,.{decimals}f}")


def fmt_price(value: float | None, currency: str = "") -> str:
    if value is None or not math.isfinite(value):
        return "–"
    symbol = _CURRENCY_SYMBOL.get(currency, currency)
    return f"{fmt_num(value)} {symbol}".strip()


def fmt_pct(value: float | None, decimals: int = 1, sign: bool = True) -> str:
    if value is None or not math.isfinite(value):
        return "–"
    text = _de(f"{value * 100:{'+' if sign else ''},.{decimals}f}")
    return f"{text} %"


def fmt_date(value: pd.Timestamp | None) -> str:
    if value is None or pd.isna(value):
        return "–"
    return pd.Timestamp(value).strftime("%d.%m.%Y")


def fmt_score(score: float) -> str:
    """Score without decimals, truncated toward zero so that the shown number always
    matches the category (e.g. -54.6 is shown as -54 and is "Verkaufen", not -55)."""
    return f"{int(score):+d}"


def fmt_days(trading_days: int) -> str:
    """Trading days as a rough calendar duration ("ca. 3 Wochen")."""
    weeks = trading_days / 5
    if weeks < 2:
        return f"{trading_days} Handelstage"
    if weeks < 9:
        return f"ca. {round(weeks)} Wochen"
    return f"ca. {round(trading_days / 21)} Monate"
