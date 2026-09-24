"""Command line version: python -m stock_analyzer [TICKER ...] [--liste DAX] [--demo]"""
from __future__ import annotations

import argparse
import sys

from .data import SyntheticProvider, YahooProvider
from .formatting import fmt_date, fmt_pct, fmt_price, fmt_score
from .fundamentals import fetch_many, synthetic_fundamentals
from .halal import HALAL, check
from .market import scan
from .scoring import BUY, HOLD
from .universes import CATALOG, UNIVERSES, search_catalog


def resolve_names(entries: list[str]) -> dict[str, str]:
    """Accept tickers or company names ("Alphabet" -> GOOGL)."""
    out = {}
    for entry in entries:
        hits = search_catalog(entry, 1)
        if hits and (entry.upper() not in CATALOG or hits[0][0] == entry.upper()):
            out[hits[0][0]] = hits[0][1]
        else:
            out[entry.upper()] = CATALOG.get(entry.upper(), entry.upper())
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m stock_analyzer",
                                     description="Stuft Aktien als Kaufen, Halten oder Verkaufen ein.")
    parser.add_argument("tickers", nargs="*", help="Yahoo-Ticker, z. B. AAPL SAP.DE (ohne Angabe: --liste)")
    parser.add_argument("--liste", default="Beliebt", choices=list(UNIVERSES), help="vordefinierte Aktienliste")
    parser.add_argument("--index", help="Vergleichsindex, z. B. ^GDAXI oder ^GSPC")
    parser.add_argument("--zeitraum", default="5y", choices=["2y", "5y", "10y"], help="Historie für die Analyse")
    parser.add_argument("--demo", action="store_true", help="simulierte Kurse statt Yahoo Finance")
    parser.add_argument("--details", action="store_true", help="Preis-Schwellen berechnen (langsamer)")
    parser.add_argument("--nur-halal", action="store_true", help="nur Aktien anzeigen, die den Halal-Check bestehen")
    args = parser.parse_args(argv)

    universe = UNIVERSES[args.liste]
    tickers = resolve_names(args.tickers) if args.tickers else universe["tickers"]
    benchmark = args.index or universe["benchmark"]
    benchmark_name = args.index or universe["benchmark_name"]
    provider = SyntheticProvider() if args.demo else YahooProvider()
    result = scan(provider, tickers, benchmark, benchmark_name, period=args.zeitraum, with_triggers=args.details)

    if result.regime:
        r = result.regime
        print(f"Marktumfeld {r.name}: {r.label} (1 Monat {fmt_pct(r.perf_1m)}, 3 Monate {fmt_pct(r.perf_3m)})\n")
    items = [(r.ticker, r.price) for r in result.recommendations]
    funda = ({t: synthetic_fundamentals(t, p) for t, p in items} if args.demo
             else fetch_many([t for t, _ in items]))
    for rec in result.recommendations:
        halal = check(rec.ticker, funda.get(rec.ticker))
        if args.nur_halal and halal.status != HALAL:
            continue
        price = fmt_price(rec.price, rec.currency)
        head = (f"{halal.icon} {rec.label_de:<15} {rec.ticker:<9} {rec.name[:22]:<22} {price:>13}  "
                f"Score {fmt_score(rec.score):>4}")
        if rec.side == BUY:
            detail = (f"Verkauf ab ca. {fmt_date(rec.horizon_date)} · Kursziel {fmt_price(rec.target_price, rec.currency)} "
                      f"({fmt_pct(rec.expected_return)}) · Stop-Loss {fmt_price(rec.stop_loss, rec.currency)}")
        elif rec.side == HOLD:
            detail = f"Halten bis ca. {fmt_date(rec.horizon_date)}"
            if rec.upper_trigger:
                detail += f" · Kaufsignal über {fmt_price(rec.upper_trigger, rec.currency)}"
            if rec.lower_trigger:
                detail += f" · Verkaufssignal unter {fmt_price(rec.lower_trigger, rec.currency)}"
        else:
            detail = f"Neubewertung frühestens ca. {fmt_date(rec.horizon_date)}"
            if rec.upper_trigger:
                detail += f" · Signal endet über {fmt_price(rec.upper_trigger, rec.currency)}"
        reasons = f"  [{' · '.join(halal.reasons)}]" if halal.reasons else ""
        print(f"{head}  {detail}{reasons}")
    for ticker, err in result.errors.items():
        print(f"Übersprungen {ticker}: {err}", file=sys.stderr)
    if not result.recommendations:
        print("Keine Kursdaten erhalten – Internetverbindung prüfen oder --demo verwenden.", file=sys.stderr)
        return 1
    print("\n✅ halal · ❌ nicht halal · ❔ prüfen (Geschäftsfeld + Debt-to-Equity ≤ 0,33)")
    print("Keine Anlageberatung. Alle Angaben sind Richtwerte aus technischer Analyse.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
