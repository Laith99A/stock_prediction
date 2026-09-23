"""Price data providers: Yahoo Finance (live) and a synthetic offline demo."""
from __future__ import annotations

import zlib
from typing import Protocol

import numpy as np
import pandas as pd

OHLCV = ["Open", "High", "Low", "Close", "Volume"]

PERIOD_DAYS = {"1y": 252, "2y": 504, "5y": 1260, "10y": 2520}


class DataProvider(Protocol):
    def history(self, tickers: list[str], period: str = "5y") -> dict[str, pd.DataFrame]:
        """Daily OHLCV history per ticker. Tickers without data are omitted."""
        ...


def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise a raw OHLCV frame: expected columns, no NaN closes, sorted, tz-naive."""
    df = df.copy()
    df.columns = [str(c).title() for c in df.columns]
    if "Close" not in df:
        return pd.DataFrame(columns=OHLCV)
    for col in ("Open", "High", "Low"):
        if col not in df:
            df[col] = df["Close"]
    if "Volume" not in df:
        df["Volume"] = 0.0
    df = df[OHLCV].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=["Close"])
    df = df[df["Close"] > 0]
    for col in ("Open", "High", "Low"):
        df[col] = df[col].fillna(df["Close"])
    df["Volume"] = df["Volume"].fillna(0.0)
    df.index = pd.DatetimeIndex(df.index)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def split_download(raw: pd.DataFrame | None, tickers: list[str]) -> dict[str, pd.DataFrame]:
    """Split a `yfinance.download` result into one frame per ticker.

    Handles both column layouts yfinance produces: (Ticker, Price) with
    group_by="ticker" and (Price, Ticker) with the default group_by="column",
    as well as flat columns for a single ticker.
    """
    if raw is None or raw.empty:
        return {}
    if not isinstance(raw.columns, pd.MultiIndex):
        frame = clean_ohlcv(raw)
        return {tickers[0]: frame} if len(tickers) == 1 and not frame.empty else {}
    if "Close" in set(raw.columns.get_level_values(0)):
        raw = raw.swaplevel(0, 1, axis=1)
    available = set(raw.columns.get_level_values(0))
    out: dict[str, pd.DataFrame] = {}
    for ticker in tickers:
        if ticker not in available:
            continue
        frame = clean_ohlcv(raw[ticker])
        if not frame.empty:
            out[ticker] = frame
    return out


class YahooProvider:
    """Live daily prices from Yahoo Finance via yfinance (dividend/split adjusted)."""

    def history(self, tickers: list[str], period: str = "5y") -> dict[str, pd.DataFrame]:
        import yfinance as yf

        tickers = list(dict.fromkeys(t.strip().upper() for t in tickers if t.strip()))
        if not tickers:
            return {}
        raw = yf.download(
            tickers,
            period=period,
            interval="1d",
            auto_adjust=True,
            group_by="ticker",
            progress=False,
            threads=True,
        )
        return split_download(raw, tickers)


class SyntheticProvider:
    """Deterministic, regime-switching random prices for offline demos and tests.

    Each ticker gets its own reproducible series (seeded from the ticker name)
    that alternates between up-, side- and downtrend phases.
    """

    def __init__(self, end: pd.Timestamp | None = None, seed: int = 0):
        self.end = pd.Timestamp(end) if end is not None else pd.Timestamp.today().normalize()
        self.seed = seed

    def history(self, tickers: list[str], period: str = "5y") -> dict[str, pd.DataFrame]:
        n = PERIOD_DAYS.get(period, 1260)
        return {t: self.series(t, n) for t in tickers if t.strip()}

    def series(self, ticker: str, n: int) -> pd.DataFrame:
        rng = np.random.default_rng(zlib.crc32(ticker.encode()) + self.seed)
        drifts = np.array([0.45, 0.10, -0.35])  # annualised: up / side / down
        rets = np.empty(n)
        i = 0
        regime = rng.integers(0, 3)
        base_vol = rng.uniform(0.18, 0.38)
        while i < n:
            length = int(rng.integers(40, 170))
            regime = rng.choice([r for r in range(3) if r != regime])
            vol = base_vol * (1.3 if regime == 2 else 1.0)
            end = min(n, i + length)
            rets[i:end] = rng.normal(drifts[regime] / 252, vol / np.sqrt(252), end - i)
            i = end
        close = float(rng.uniform(20, 400)) * np.exp(np.cumsum(rets))
        spread = np.abs(rng.normal(0, base_vol / np.sqrt(252) * 0.6, n))
        open_ = close * np.exp(rng.normal(0, base_vol / np.sqrt(252) * 0.4, n))
        high = np.maximum(open_, close) * (1 + spread)
        low = np.minimum(open_, close) * (1 - spread)
        volume = rng.lognormal(14, 0.3, n) * (1 + 20 * np.abs(rets))
        index = pd.bdate_range(end=self.end, periods=n)
        return pd.DataFrame(
            {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume.round()},
            index=index,
        )


_SUFFIX_CURRENCY = {
    "DE": "EUR", "F": "EUR", "PA": "EUR", "AS": "EUR", "MI": "EUR", "MC": "EUR",
    "BR": "EUR", "VI": "EUR", "HE": "EUR", "LS": "EUR", "IR": "EUR",
    "L": "GBp", "SW": "CHF", "TO": "CAD", "T": "JPY", "HK": "HKD", "AX": "AUD",
    "ST": "SEK", "CO": "DKK", "OL": "NOK",
}


def guess_currency(ticker: str) -> str:
    """Trading currency from the Yahoo ticker suffix (e.g. SAP.DE → EUR)."""
    if ticker.startswith("^"):
        return ""
    if "." in ticker:
        return _SUFFIX_CURRENCY.get(ticker.rsplit(".", 1)[1].upper(), "")
    return "USD"
