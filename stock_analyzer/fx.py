"""Currency conversion to euro, so prices from all markets can be compared."""
from __future__ import annotations

import math

# Rough rates (units per 1 EUR) for the offline demo mode.
DEMO_RATES = {"USD": 1.10, "HKD": 8.55, "GBP": 0.85, "CHF": 0.94, "DKK": 7.46, "SEK": 11.2, "NOK": 11.6}


def fx_tickers(currencies: set[str]) -> dict[str, str]:
    """Yahoo symbols (e.g. EURUSD=X) for the currencies that need a rate."""
    out = {}
    for currency in currencies:
        code = "GBP" if currency == "GBp" else currency
        if code and code != "EUR":
            out[code] = f"EUR{code}=X"
    return out


def to_eur(price: float | None, currency: str, rates: dict[str, float]) -> float | None:
    """Convert a price to euro. `rates` holds units of the currency per 1 EUR."""
    if price is None or not math.isfinite(price):
        return None
    if currency == "EUR":
        return price
    if currency == "GBp":  # London quotes in pence
        price, currency = price / 100.0, "GBP"
    rate = rates.get(currency)
    if not rate:
        return None
    return price / rate
