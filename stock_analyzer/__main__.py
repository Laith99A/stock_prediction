"""Command line version: python -m stock_analyzer [TICKER ...] [--liste DAX] [--demo]"""
from __future__ import annotations

import argparse
import sys

from .data import SyntheticProvider, YahooProvider
from .formatting import fmt_date, fmt_pct, fmt_price
from .market import scan
from .scoring import BUY, HOLD
from .universes import UNIVERSES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m stock_analyzer",
                                     description="Stuft Aktien als Kaufen, Halten oder Verkaufen ein.")
    parser.add_argument("tickers", nargs="*", help="Yahoo-Ticker, z. B. AAPL SAP.DE (ohne Angabe: --liste)")
    parser.add_argument("--liste", default="DAX", choices=list(UNIVERSES), help="vordefinierte Aktienliste")
    parser.add_argument("--index", help="Vergleichsindex, z. B. ^GDAXI oder ^GSPC")
    parser.add_argument("--zeitraum", default="5y", choices=["2y", "5y", "10y"], help="Historie für die Analyse")
    parser.add_argument("--demo", action="store_true", help="simulierte Kurse statt Yahoo Finance")
    parser.add_argument("--details", action="store_true", help="Preis-Schwellen berechnen (langsamer)")
    args = parser.parse_args(argv)

    universe = UNIVERSES[args.liste]
    tickers = {t.upper(): t.upper() for t in args.tickers} if args.tickers else universe["tickers"]
    benchmark = args.index or universe["benchmark"]
    benchmark_name = args.index or universe["benchmark_name"]
    provider = SyntheticProvider() if args.demo else YahooProvider()
    result = scan(provider, tickers, benchmark, benchmark_name, period=args.zeitraum, with_triggers=args.details)

    if result.regime:
        r = result.regime
        print(f"Marktumfeld {r.name}: {r.label} (1 Monat {fmt_pct(r.perf_1m)}, 3 Monate {fmt_pct(r.perf_3m)})\n")
    for rec in result.recommendations:
        price = fmt_price(rec.price, rec.currency)
        head = f"{rec.label_de:<9} {rec.ticker:<9} {rec.name[:22]:<22} {price:>13}  Score {rec.score:+4.0f}"
        if rec.label == BUY:
            detail = (f"Verkauf ab ca. {fmt_date(rec.horizon_date)} · Kursziel {fmt_price(rec.target_price, rec.currency)} "
                      f"({fmt_pct(rec.expected_return)}) · Stop-Loss {fmt_price(rec.stop_loss, rec.currency)}")
        elif rec.label == HOLD:
            detail = f"Halten bis ca. {fmt_date(rec.horizon_date)}"
            if rec.upper_trigger:
                detail += f" · Kaufsignal über {fmt_price(rec.upper_trigger, rec.currency)}"
            if rec.lower_trigger:
                detail += f" · Verkaufssignal unter {fmt_price(rec.lower_trigger, rec.currency)}"
        else:
            detail = f"Neubewertung frühestens ca. {fmt_date(rec.horizon_date)}"
            if rec.upper_trigger:
                detail += f" · Signal endet über {fmt_price(rec.upper_trigger, rec.currency)}"
        print(f"{head}  {detail}")
    for ticker, err in result.errors.items():
        print(f"Übersprungen {ticker}: {err}", file=sys.stderr)
    if not result.recommendations:
        print("Keine Kursdaten erhalten – Internetverbindung prüfen oder --demo verwenden.", file=sys.stderr)
        return 1
    print("\nKeine Anlageberatung. Alle Angaben sind Richtwerte aus technischer Analyse.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
