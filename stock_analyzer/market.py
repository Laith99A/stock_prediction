"""Market scan: analyse a list of stocks against a benchmark index."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import indicators as ind
from .data import DataProvider, guess_currency
from .recommendation import InsufficientDataError, Recommendation, analyze
from .scoring import trend_component


@dataclass
class MarketRegime:
    name: str
    level: float
    trend: float  # -1..1
    above_sma200: bool
    perf_1m: float
    perf_3m: float

    @property
    def label(self) -> str:
        if self.trend > 0.3:
            return "Aufwärtstrend"
        if self.trend < -0.3:
            return "Abwärtstrend"
        return "Seitwärts"

    @property
    def short_label(self) -> str:
        return {"Aufwärtstrend": "↗ Aufwärts", "Abwärtstrend": "↘ Abwärts", "Seitwärts": "→ Seitwärts"}[self.label]


@dataclass
class ScanResult:
    recommendations: list[Recommendation]
    histories: dict[str, pd.DataFrame]
    benchmark: pd.Series | None
    regime: MarketRegime | None
    errors: dict[str, str] = field(default_factory=dict)

    def table(self) -> pd.DataFrame:
        return recommendations_table(self.recommendations)


def market_regime(benchmark: pd.Series | None, name: str) -> MarketRegime | None:
    if benchmark is None or len(benchmark.dropna()) < 60:
        return None
    close = benchmark.dropna()
    trend = float(trend_component(close).iloc[-1])
    sma200 = ind.sma(close, 200).iloc[-1]
    return MarketRegime(
        name=name,
        level=float(close.iloc[-1]),
        trend=trend if np.isfinite(trend) else 0.0,
        above_sma200=bool(np.isfinite(sma200) and close.iloc[-1] > sma200),
        perf_1m=float(ind.rate_of_change(close, 21).iloc[-1]),
        perf_3m=float(ind.rate_of_change(close, 63).iloc[-1]),
    )


def scan(
    provider: DataProvider,
    tickers: dict[str, str] | list[str],
    benchmark_ticker: str | None,
    benchmark_name: str = "",
    period: str = "5y",
    with_triggers: bool = False,
) -> ScanResult:
    names = tickers if isinstance(tickers, dict) else {t: t for t in tickers}
    symbols = list(names)
    wanted = symbols + ([benchmark_ticker] if benchmark_ticker else [])
    histories = provider.history(wanted, period=period)

    benchmark = None
    if benchmark_ticker and benchmark_ticker in histories:
        benchmark = histories.pop(benchmark_ticker)["Close"]

    recs: list[Recommendation] = []
    errors: dict[str, str] = {}
    for ticker in symbols:
        df = histories.get(ticker)
        if df is None or df.empty:
            errors[ticker] = "keine Kursdaten gefunden"
            continue
        try:
            recs.append(
                analyze(
                    df,
                    ticker,
                    name=names[ticker],
                    currency=guess_currency(ticker),
                    benchmark=benchmark,
                    with_triggers=with_triggers,
                )
            )
        except InsufficientDataError as exc:
            errors[ticker] = str(exc)
    recs.sort(key=lambda r: r.score, reverse=True)
    return ScanResult(
        recommendations=recs,
        histories=histories,
        benchmark=benchmark,
        regime=market_regime(benchmark, benchmark_name or (benchmark_ticker or "")),
        errors=errors,
    )


def recommendations_table(recs: list[Recommendation]) -> pd.DataFrame:
    rows = []
    for r in recs:
        rows.append(
            {
                "Ticker": r.ticker,
                "Name": r.name,
                "Empfehlung": r.label_text,
                "Score": r.score,
                # Buy side: sell from this date · Hold: hold until · Sell side: re-evaluate from
                "Datum": r.horizon_date,
                "Kurs": r.price,
                "Währung": r.currency,
                "Kursziel": r.target_price,
                "Potenzial": r.expected_return,
                "Stop-Loss": r.stop_loss,
                "Signalstärke": r.strength,
                "Seit (Tage)": r.signal_age,
                "Tendenz": r.tendency,
                "Label": r.label,
            }
        )
    return pd.DataFrame(rows)
