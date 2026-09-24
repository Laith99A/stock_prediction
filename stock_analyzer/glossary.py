"""Plain-language explanations for every term shown in the app.

`short` is used for tooltips, `long` and `example` for the glossary tab.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Term:
    title: str
    category: str
    short: str
    long: str
    example: str = ""


EMPFEHLUNG = "Empfehlungen"
APP = "Zahlen in dieser App"
RISIKO = "Risiko"
INDIKATOR = "Indikatoren (Signale aus dem Kursverlauf)"
BASIS = "Börsen-Grundbegriffe"
RUECKBLICK = "Rückblick"

CATEGORIES = [EMPFEHLUNG, APP, RISIKO, INDIKATOR, BASIS, RUECKBLICK]

TERMS: dict[str, Term] = {
    # ------------------------------------------------------------------ recommendations
    "stark_kaufen": Term(
        "Stark kaufen (Strong Buy)", EMPFEHLUNG,
        "Signal-Score ab +55: Fast alle Faktoren zeigen deutlich nach oben.",
        "Die stärkste positive Einstufung. Trend, Momentum und Marktumfeld sind klar positiv. "
        "Die App nennt dir zusätzlich, ab wann ein Verkauf empfohlen ist, ein Kursziel und einen Stop-Loss.",
        "Score +68 → Stark kaufen.",
    ),
    "kaufen": Term(
        "Kaufen (Buy)", EMPFEHLUNG,
        "Signal-Score zwischen +25 und +55: Das Gesamtbild ist positiv.",
        "Die meisten Faktoren sind positiv, aber nicht so eindeutig wie bei „Stark kaufen“. "
        "Auch hier bekommst du Verkaufsdatum, Kursziel und Stop-Loss.",
        "Score +38 → Kaufen.",
    ),
    "halten": Term(
        "Halten (Hold)", EMPFEHLUNG,
        "Signal-Score zwischen −25 und +25: kein klares Signal – abwarten.",
        "Die Faktoren widersprechen sich oder sind neutral. Wer die Aktie hat, behält sie; wer sie nicht hat, "
        "wartet ab. Die App sagt, bis wann ungefähr, und bei welchen Kursen ein Kauf- oder Verkaufssignal entstehen würde.",
        "Score +5 → Halten bis ca. 14.10.",
    ),
    "verkaufen": Term(
        "Verkaufen (Sell)", EMPFEHLUNG,
        "Signal-Score zwischen −55 und −25: Das Gesamtbild ist negativ.",
        "Die meisten Faktoren zeigen nach unten. Die App empfiehlt, die Aktie zu verkaufen bzw. nicht zu kaufen, "
        "und nennt den Kurs, ab dem das Verkaufssignal enden würde.",
    ),
    "stark_verkaufen": Term(
        "Stark verkaufen (Strong Sell)", EMPFEHLUNG,
        "Signal-Score bis −55: Fast alle Faktoren zeigen deutlich nach unten.",
        "Die stärkste negative Einstufung – typischerweise ein klarer Abwärtstrend in einem schwachen Umfeld.",
    ),
    # ------------------------------------------------------------------ app numbers
    "score": Term(
        "Signal-Score", APP,
        "Gesamtnote von −100 (sehr negativ) bis +100 (sehr positiv) aus sieben Faktoren.",
        "Jeder Faktor (Trend, Momentum, RSI, 52-Wochen-Hoch, Volumen, relative Stärke, Marktumfeld) wird "
        "zwischen −100 und +100 bewertet und gewichtet zusammengezählt. Der Score wird über etwa eine Woche "
        "geglättet, damit die Empfehlung nicht täglich springt. Daraus folgt die Einstufung: ab +55 Stark kaufen, "
        "ab +25 Kaufen, bis −25 Verkaufen, bis −55 Stark verkaufen, dazwischen Halten.",
    ),
    "signalstaerke": Term(
        "Signalstärke", APP,
        "Wie eindeutig die Empfehlung ist (0–100 %).",
        "Setzt sich zusammen aus dem Abstand des Scores zur Schwelle und dem Anteil der Faktoren, die in "
        "dieselbe Richtung zeigen. Hohe Signalstärke = klares Bild, niedrige = knappe Entscheidung.",
    ),
    "zeithorizont": Term(
        "Verkauf ab / Halten bis", APP,
        "Kaufen: ab wann der Verkauf empfohlen ist. Halten: ungefähr bis wann halten.",
        "Die App schätzt, wie lange das aktuelle Signal noch gilt – aus der Dauer früherer Signale dieser Aktie "
        "und aus der Richtung, in die sich der Score gerade bewegt. Bei „Verkaufen“ ist es der früheste Termin "
        "für eine Neubewertung. Das Datum ist ein Richtwert, kein fester Termin.",
    ),
    "kursziel": Term(
        "Kursziel (Take-Profit)", APP,
        "Kurs, bei dem du Gewinne mitnehmen und verkaufen solltest – auch vor dem Verkaufsdatum.",
        "Berechnet aus dem bisherigen Aufwärtstrend (vorsichtig nur zur Hälfte fortgeschrieben), mindestens aber "
        "3 × ATR über dem aktuellen Kurs. Wird das Ziel erreicht, ist der erwartete Gewinn eingefahren.",
        "Kurs 100 €, Kursziel 110 € → bei 110 € verkaufen.",
    ),
    "stop_loss": Term(
        "Stop-Loss", APP,
        "Verlustgrenze: Fällt der Kurs darunter, sofort verkaufen.",
        "Liegt 2 × ATR (zwei durchschnittliche Tagesschwankungen) unter dem Kurs. Schützt vor großen Verlusten, "
        "falls die Einschätzung falsch war. Viele Broker bieten dafür eine automatische Stop-Loss-Order an.",
        "Kurs 100 €, Stop-Loss 94 € → fällt die Aktie unter 94 €, verkaufen.",
    ),
    "potenzial": Term(
        "Potenzial", APP,
        "Wie viel Prozent der Kurs bis zum Kursziel steigen müsste.",
        "Abstand zwischen aktuellem Kurs und Kursziel in Prozent.",
        "Kurs 100 €, Kursziel 110 € → Potenzial +10 %.",
    ),
    "chance_risiko": Term(
        "Chance-Risiko-Verhältnis", APP,
        "Möglicher Gewinn bis zum Kursziel geteilt durch möglichen Verlust bis zum Stop-Loss.",
        "Ein Wert von 1,5 heißt: Der mögliche Gewinn ist 1,5-mal so groß wie der mögliche Verlust. "
        "Werte über 1 sind günstig.",
        "Ziel +9 %, Stop-Loss −6 % → Chance/Risiko 1,5.",
    ),
    "signal_seit": Term(
        "Signal aktiv seit", APP,
        "Seit wie vielen Handelstagen die Aktie auf dieser Seite (Kaufen, Halten, Verkaufen) steht.",
        "Ein Wechsel von „Stark kaufen“ zu „Kaufen“ zählt nicht als neues Signal – beides ist die Kauf-Seite.",
    ),
    "tendenz": Term(
        "Tendenz", APP,
        "Ob der Score in den letzten 10 Handelstagen gestiegen, gefallen oder gleich geblieben ist.",
        "Steigt der Score, verbessert sich das Bild – bei „Halten“ geht es dann eher Richtung Kaufen.",
    ),
    "preis_schwelle": Term(
        "Kaufsignal über / Verkaufssignal unter", APP,
        "Kurs, ab dem die Empfehlung wechseln würde, wenn die Aktie ihn innerhalb einer Woche erreicht.",
        "Die App rechnet durch, wie sich der Score verändert, wenn der Kurs in den nächsten Tagen auf ein "
        "bestimmtes Niveau steigt oder fällt, und sucht den Kurs, an dem die Schwelle überschritten wird.",
    ),
    # ------------------------------------------------------------------ risk
    "volatilitaet": Term(
        "Volatilität", RISIKO,
        "Wie stark der Kurs schwankt – hochgerechnet aufs Jahr. Höher = riskanter.",
        "Gemessen als Schwankungsbreite der täglichen Kursänderungen der letzten 3 Monate, umgerechnet auf ein "
        "Jahr. Faustregel: unter 20 % ruhig (z. B. große Konsumwerte), 20–40 % normal, über 40 % sehr schwankungsreich "
        "(z. B. junge Tech-Werte).",
        "Volatilität 30 % → Kursschwankungen von rund ±30 % innerhalb eines Jahres sind nicht ungewöhnlich.",
    ),
    "atr": Term(
        "ATR (Average True Range)", RISIKO,
        "Durchschnittliche Tagesschwankung der Aktie in Euro/Dollar (letzte 14 Tage).",
        "Misst, wie weit sich der Kurs an einem typischen Tag bewegt – inklusive Kurslücken über Nacht. "
        "Die App nutzt die ATR für Stop-Loss und Mindest-Kursziel, damit diese zur Schwankung der Aktie passen.",
        "ATR 3 € bei Kurs 100 € → die Aktie bewegt sich typischerweise um ca. 3 € am Tag.",
    ),
    "max_verlust": Term(
        "Maximaler Verlust (Drawdown)", RISIKO,
        "Größter Rückgang vom bisherigen Höchststand bis zum Tiefpunkt.",
        "Zeigt den schlimmsten Zwischenverlust, den man im betrachteten Zeitraum hätte aushalten müssen.",
        "Depot steigt auf 150 €, fällt dann auf 105 € → maximaler Verlust −30 %.",
    ),
    # ------------------------------------------------------------------ indicators
    "trend": Term(
        "Trend", INDIKATOR,
        "Die grundsätzliche Richtung des Kurses über Wochen und Monate.",
        "Bewertet über die Lage des Kurses zur 50- und 200-Tage-Linie und deren Steigung. "
        "Aktien im Aufwärtstrend steigen statistisch häufiger weiter („The trend is your friend“).",
    ),
    "gleitender_durchschnitt": Term(
        "50-/200-Tage-Linie", INDIKATOR,
        "Durchschnittskurs der letzten 50 bzw. 200 Handelstage.",
        "Glättet die täglichen Schwankungen. Liegt der Kurs über der 200-Tage-Linie, gilt der langfristige Trend "
        "als intakt; darunter als angeschlagen. Die 50-Tage-Linie zeigt den mittelfristigen Trend.",
    ),
    "golden_cross": Term(
        "Golden Cross / Death Cross", INDIKATOR,
        "50-Tage-Linie über (Golden) bzw. unter (Death) der 200-Tage-Linie.",
        "Golden Cross gilt als Zeichen für einen Aufwärtstrend, Death Cross für einen Abwärtstrend.",
    ),
    "momentum": Term(
        "Momentum", INDIKATOR,
        "Wie stark die Aktie zuletzt gestiegen oder gefallen ist (3 und 6 Monate) – und ob sich das beschleunigt.",
        "Kombiniert die Kursentwicklung der letzten 3 und 6 Monate mit dem MACD. Aktien mit starkem Momentum "
        "entwickeln sich statistisch oft eine Zeit lang weiter gut.",
    ),
    "macd": Term(
        "MACD", INDIKATOR,
        "Zeigt, ob sich eine Kursbewegung beschleunigt oder abschwächt.",
        "Differenz zweier gleitender Durchschnitte (12 und 26 Tage). Liegt der MACD über seiner Signallinie, "
        "nimmt die Aufwärtsdynamik zu; darunter lässt sie nach.",
    ),
    "rsi": Term(
        "RSI (Relative-Stärke-Index)", INDIKATOR,
        "Wert von 0–100: über 70 „überkauft“ (evtl. zu schnell gestiegen), unter 30 „überverkauft“.",
        "Vergleicht die Gewinne mit den Verlusten der letzten 14 Tage. Ein sehr hoher RSI warnt vor einer "
        "Verschnaufpause, ein sehr niedriger deutet auf Erholungspotenzial hin. 50–70 gilt als gesunde Stärke.",
        "RSI 78 → Aktie ist heiß gelaufen, Rücksetzer möglich.",
    ),
    "hoch_52w": Term(
        "52-Wochen-Hoch", INDIKATOR,
        "Höchster Kurs der letzten 12 Monate – und wie weit die Aktie davon entfernt ist.",
        "Aktien nahe ihrem Jahreshoch sind oft stark gefragt. Liegt eine Aktie weit darunter, "
        "steckt sie meist in einer Schwächephase.",
        "Hoch 120 €, Kurs 114 € → 5 % unter dem 52-Wochen-Hoch.",
    ),
    "volumen": Term(
        "Volumen (On-Balance-Volume)", INDIKATOR,
        "Ob an Tagen mit Kursgewinnen mehr gehandelt wird als an Tagen mit Verlusten.",
        "Steigende Kurse bei hohem Handelsvolumen gelten als „bestätigt“ – viele Anleger kaufen mit. "
        "Hohes Volumen an Verlusttagen deutet auf Abgabedruck hin.",
    ),
    "relative_staerke": Term(
        "Relative Stärke", INDIKATOR,
        "Wie sich die Aktie im Vergleich zum Gesamtmarkt (Index) entwickelt hat.",
        "Vergleicht die Performance der Aktie mit dem Vergleichsindex über 3 und 6 Monate. "
        "Positiv = besser als der Markt. (Nicht zu verwechseln mit dem RSI.)",
        "Aktie +12 %, Index +5 % → relative Stärke +7 Prozentpunkte.",
    ),
    "marktumfeld": Term(
        "Marktumfeld", INDIKATOR,
        "Trend des Gesamtmarkts (Vergleichsindex) – in einem fallenden Markt fallen auch gute Aktien oft mit.",
        "Wird wie der Trend einer Aktie bewertet, aber für den Index (z. B. DAX oder S&P 500). "
        "Fließt als eigener Faktor in jeden Score ein.",
    ),
    # ------------------------------------------------------------------ basics
    "ticker": Term(
        "Ticker (Kürzel)", BASIS,
        "Kurzname einer Aktie an der Börse, z. B. SAP.DE oder AAPL.",
        "Die App nutzt die Kürzel von Yahoo Finance. Deutsche Aktien enden auf .DE (Xetra), US-Aktien haben "
        "keine Endung, Paris .PA, Amsterdam .AS, Zürich .SW, London .L. Du kannst aber auch einfach nach dem "
        "Firmennamen suchen.",
    ),
    "index": Term(
        "Index / Vergleichsindex", BASIS,
        "Ein Korb aus vielen Aktien, der den Gesamtmarkt abbildet – z. B. DAX, S&P 500 oder MSCI World.",
        "Dient als Maßstab: Entwickelt sich eine Aktie besser als ihr Index, ist sie relativ stark.",
    ),
    "handelstag": Term(
        "Handelstag", BASIS,
        "Tag, an dem die Börse geöffnet ist (Montag–Freitag ohne Feiertage).",
        "Ein Monat hat rund 21 Handelstage, ein Jahr rund 252.",
    ),
    "performance": Term(
        "Performance", BASIS,
        "Kursveränderung in Prozent über einen Zeitraum.",
        "Die App nutzt dividendenbereinigte Kurse – Dividenden sind also eingerechnet.",
        "3-Monats-Performance +8 % → die Aktie ist in 3 Monaten um 8 % gestiegen.",
    ),
    # ------------------------------------------------------------------ backtest
    "rueckblick": Term(
        "Rückblick (Backtest)", RUECKBLICK,
        "Wie gut die Signale dieser App bei dieser Aktie in der Vergangenheit funktioniert hätten.",
        "Die App wendet ihre Regeln auf die vergangenen Kurse an und prüft, was danach passiert ist. "
        "Das ist ein Plausibilitäts-Check – gute Ergebnisse in der Vergangenheit garantieren keine in der Zukunft.",
    ),
    "strategie": Term(
        "Strategie vs. Kaufen & Liegenlassen", RUECKBLICK,
        "Strategie: nur investiert, solange „Kaufen“ oder „Stark kaufen“ gilt. Liegenlassen: immer investiert.",
        "Vergleicht, ob das Befolgen der Signale besser gewesen wäre als die Aktie einfach zu halten "
        "(ohne Gebühren und Steuern).",
    ),
    "anteil_im_plus": Term(
        "Anteil im Plus", RUECKBLICK,
        "Wie oft der Kurs einen Monat nach dem Signal höher lag als am Signaltag.",
        "Bei Kaufsignalen sollte dieser Wert möglichst hoch sein, bei Verkaufssignalen möglichst niedrig.",
    ),
}


def tip(key: str) -> str:
    """Short explanation for tooltips (help=...)."""
    return TERMS[key].short
