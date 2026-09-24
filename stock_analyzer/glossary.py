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
KENNZAHL = "Kennzahlen (Fundamentaldaten)"
CHART = "Chartanalyse"
HALAL = "☪️ Halal investieren"
SLANG = "💬 Investor-Sprache"

CATEGORIES = [HALAL, SLANG, EMPFEHLUNG, APP, KENNZAHL, RISIKO, INDIKATOR, CHART, BASIS, RUECKBLICK]

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

    # ------------------------------------------------------------------ fundamentals
    "fundamentalanalyse": Term(
        "Fundamentalanalyse vs. technische Analyse", KENNZAHL,
        "Fundamental: Wie gut ist das Unternehmen und wie teuer die Aktie? Technisch: Was sagt der Kursverlauf?",
        "Die Empfehlung der App beruht auf der technischen Analyse (Kursverlauf). Die Kennzahlen ergänzen das "
        "Bild: Eine technisch starke Aktie mit sehr hoher Bewertung oder hohen Schulden ist riskanter als eine "
        "mit soliden Zahlen.",
    ),
    "verschuldungsgrad": Term(
        "Verschuldungsgrad (Debt-to-Equity)", KENNZAHL,
        "Schulden geteilt durch Eigenkapital. Unter 1 solide, über 2 hoch verschuldet.",
        "Zeigt, wie stark ein Unternehmen mit fremdem Geld (Krediten, Anleihen) statt mit eigenem Geld arbeitet. "
        "Viele Schulden machen anfällig für steigende Zinsen und schlechte Zeiten. Ein negativer Wert bedeutet "
        "negatives Eigenkapital (z. B. durch hohe Aktienrückkäufe oder Verluste). Bei Banken und Versicherern "
        "ist die Kennzahl wegen ihres Geschäftsmodells kaum vergleichbar.",
        "Schulden 150 Mrd., Eigenkapital 100 Mrd. → Debt-to-Equity 1,5.",
    ),
    "liquiditaet": Term(
        "Liquidität (Current Ratio)", KENNZAHL,
        "Kurzfristiges Vermögen geteilt durch kurzfristige Schulden. Über 1,5 komfortabel, unter 1 knapp.",
        "Zeigt, ob das Unternehmen die Rechnungen der nächsten 12 Monate aus Bargeld, Forderungen und Vorräten "
        "bezahlen kann.",
        "Current Ratio 2 → doppelt so viel kurzfristiges Vermögen wie kurzfristige Schulden.",
    ),
    "kgv": Term(
        "KGV (Kurs-Gewinn-Verhältnis, P/E)", KENNZAHL,
        "Aktienkurs geteilt durch Gewinn je Aktie – wie viele Jahresgewinne man für die Aktie bezahlt.",
        "Die bekannteste Bewertungskennzahl. Faustregel: unter 15 günstig, 15–25 fair, über 25 teuer. "
        "Wachstumsfirmen (z. B. Tech) haben oft ein hohes KGV, weil hohe künftige Gewinne erwartet werden. "
        "Bei Verlusten gibt es kein sinnvolles KGV.",
        "Kurs 100 €, Gewinn je Aktie 5 € → KGV 20.",
    ),
    "kgv_erwartet": Term(
        "Erwartetes KGV (Forward P/E)", KENNZAHL,
        "Wie das KGV, aber mit dem von Analysten erwarteten Gewinn der nächsten 12 Monate.",
        "Liegt das erwartete KGV deutlich unter dem aktuellen, rechnen Analysten mit steigenden Gewinnen.",
    ),
    "peg": Term(
        "PEG-Ratio", KENNZAHL,
        "KGV geteilt durch das erwartete Gewinnwachstum. Unter 1 günstig, über 2 teuer.",
        "Berücksichtigt, dass schnell wachsende Firmen ein höheres KGV verdienen. Ein KGV von 30 bei 30 % "
        "Wachstum ergibt PEG 1 – fair.",
    ),
    "kbv": Term(
        "KBV (Kurs-Buchwert-Verhältnis, P/B)", KENNZAHL,
        "Aktienkurs geteilt durch das Eigenkapital je Aktie. Unter 1 heißt: Aktie kostet weniger als ihr Buchwert.",
        "Der Buchwert ist grob das, was nach Abzug aller Schulden übrig bliebe. Ein KBV unter 1 kann ein "
        "Schnäppchen sein – oder ein Zeichen, dass der Markt Probleme erwartet. Firmen mit wenig Sachvermögen "
        "(Software, Marken) haben naturgemäß ein hohes KBV.",
        "Kurs 30 €, Buchwert je Aktie 20 € → KBV 1,5.",
    ),
    "kuv": Term(
        "KUV (Kurs-Umsatz-Verhältnis, P/S)", KENNZAHL,
        "Börsenwert geteilt durch Jahresumsatz. Nützlich, wenn eine Firma noch keinen Gewinn macht.",
        "Faustregel: unter 1 günstig, 1–4 fair, über 4 teuer – stark branchenabhängig.",
    ),
    "ev_ebitda": Term(
        "EV/EBITDA", KENNZAHL,
        "Unternehmenswert (inkl. Schulden) geteilt durch den operativen Gewinn vor Abschreibungen.",
        "Vergleicht Firmen unabhängig davon, wie stark sie verschuldet sind. Unter 8 günstig, über 15 teuer.",
    ),
    "eigenkapitalrendite": Term(
        "Eigenkapitalrendite (ROE)", KENNZAHL,
        "Gewinn geteilt durch Eigenkapital – wie viel das Unternehmen aus dem Geld der Aktionäre macht.",
        "Über 15 % gilt als stark. Vorsicht: Sehr hohe Werte können auch durch sehr wenig Eigenkapital "
        "(hohe Schulden, Aktienrückkäufe) entstehen – deshalb zusammen mit dem Verschuldungsgrad ansehen.",
    ),
    "nettomarge": Term(
        "Nettomarge", KENNZAHL,
        "Wie viel vom Umsatz als Gewinn übrig bleibt.",
        "Nettomarge 20 % heißt: Von 100 € Umsatz bleiben 20 € Gewinn. Hohe Margen sprechen für "
        "Preissetzungsmacht.",
    ),
    "umsatzwachstum": Term(
        "Umsatzwachstum", KENNZAHL,
        "Wie stark der Umsatz im Vergleich zum Vorjahr gewachsen ist.",
        "Über 10 % gilt als starkes Wachstum. Schrumpfender Umsatz ist ein Warnsignal.",
    ),
    "gewinnwachstum": Term(
        "Gewinnwachstum", KENNZAHL,
        "Wie stark der Gewinn im Vergleich zum Vorjahr gewachsen ist.",
        "Steigende Gewinne sind langfristig der wichtigste Treiber für steigende Aktienkurse.",
    ),
    "dividendenrendite": Term(
        "Dividendenrendite", KENNZAHL,
        "Jährliche Dividende geteilt durch den Aktienkurs.",
        "2–6 % gelten als attraktiv. Sehr hohe Renditen entstehen oft, weil der Kurs stark gefallen ist – dann "
        "prüfen, ob die Dividende gehalten werden kann (Ausschüttungsquote).",
        "Dividende 3 € je Aktie, Kurs 100 € → Dividendenrendite 3 %.",
    ),
    "ausschuettungsquote": Term(
        "Ausschüttungsquote", KENNZAHL,
        "Welcher Anteil des Gewinns als Dividende ausgezahlt wird.",
        "Unter 60 % ist die Dividende gut gedeckt. Über 90 % zahlt die Firma fast alles aus – bei einem "
        "Gewinneinbruch droht eine Kürzung.",
    ),
    "beta": Term(
        "Beta", KENNZAHL,
        "Wie stark die Aktie im Vergleich zum Gesamtmarkt schwankt. 1 = wie der Markt.",
        "Beta 1,5: Fällt der Markt um 10 %, fällt die Aktie typischerweise um 15 %. Beta 0,6: nur um 6 %.",
    ),
    "marktkapitalisierung": Term(
        "Börsenwert (Marktkapitalisierung)", KENNZAHL,
        "Aktienkurs × Anzahl aller Aktien – was das ganze Unternehmen an der Börse kostet.",
        "Über 10 Mrd. spricht man von Large Caps (groß, meist stabiler), 2–10 Mrd. Mid Caps, darunter Small Caps.",
    ),
    "analystenziel": Term(
        "Kursziel der Analysten", KENNZAHL,
        "Durchschnittliches Kursziel von Bankanalysten für die nächsten 12 Monate.",
        "Eine Orientierung, keine Garantie – Analysten liegen oft daneben und sind im Schnitt eher zu optimistisch. "
        "Nicht zu verwechseln mit dem Kursziel dieser App, das aus dem Kursverlauf berechnet wird.",
    ),
    # ------------------------------------------------------------------ chart reading
    "unterstuetzung_widerstand": Term(
        "Unterstützung & Widerstand", CHART,
        "Kursniveaus, an denen die Aktie früher mehrfach gedreht hat – wie ein Boden bzw. eine Decke.",
        "An einer Unterstützung haben früher viele gekauft, an einem Widerstand viele verkauft. Diese Niveaus "
        "wirken oft erneut. Wird ein Widerstand durchbrochen, wird er häufig zur neuen Unterstützung.",
    ),
    "ausbruch": Term(
        "Ausbruch (Breakout)", CHART,
        "Der Kurs steigt klar über einen Widerstand oder auf ein neues Hoch.",
        "Oft der Start einer neuen Aufwärtsbewegung – besonders, wenn dabei viel gehandelt wird (hohes Volumen). "
        "Das Gegenstück ist der Bruch einer Unterstützung nach unten.",
    ),
    "hochs_tiefs": Term(
        "Höhere Hochs & höhere Tiefs", CHART,
        "Das Kennzeichen eines Aufwärtstrends: jede Welle endet höher als die vorige.",
        "Im Abwärtstrend ist es umgekehrt (tiefere Hochs und tiefere Tiefs). Bricht das Muster, endet der Trend "
        "oft.",
    ),
    "divergenz": Term(
        "Divergenz", CHART,
        "Kurs und Indikator (z. B. RSI) laufen auseinander – etwa neues Kurshoch, aber kein neues RSI-Hoch.",
        "Deutet darauf hin, dass der Schwung nachlässt und der Trend bald drehen könnte.",
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
    # ------------------------------------------------------------------ halal
    "halal_investieren": Term(
        "Halal investieren (Shariah-konform)", HALAL,
        "Investieren nach islamischen Regeln: keine verbotenen Geschäftsfelder und keine hohe Verschuldung.",
        "Die App prüft zwei Dinge: 1) Das Geschäftsfeld – ausgeschlossen sind Alkohol, Tabak, Waffen, Glücksspiel, "
        "Banken und Kredite (Zinsen), konventionelle Versicherungen, Schweinefleisch und Erwachsenenunterhaltung. "
        "2) Die Schulden – Debt-to-Equity höchstens 0,33. Nur wenn beides passt, gilt die Aktie als halal.",
    ),
    "riba": Term(
        "Riba (Zinsen)", HALAL,
        "Zinsen zu nehmen oder zu zahlen ist im Islam verboten.",
        "Deshalb fallen Banken, Kreditanbieter und Anleihen heraus. Auch Unternehmen, die sich stark über "
        "verzinste Kredite finanzieren, werden aussortiert – das misst die Schuldengrenze.",
    ),
    "halal_schulden": Term(
        "Schuldengrenze 33 %", HALAL,
        "Die App lässt nur Aktien zu, deren Schulden höchstens 33 % des Eigenkapitals betragen (Debt-to-Equity ≤ 0,33).",
        "Das ist eine strenge Regel. Viele islamische Indizes (z. B. Dow Jones Islamic, S&P Shariah) messen die "
        "Schulden stattdessen am Börsenwert – dadurch bestehen dort mehr Aktien den Test.",
        "Schulden 20 Mrd., Eigenkapital 100 Mrd. → Debt-to-Equity 0,20 → besteht.",
    ),
    "halal_pruefen": Term(
        "❔ Prüfen (Grenzfall)", HALAL,
        "Geschäftsfelder, die Gelehrte unterschiedlich bewerten, oder fehlende Daten.",
        "Beispiele: Musik- und Filmunterhaltung, Krypto-Geschäft, kleine Rüstungsanteile oder Hotels mit "
        "Alkoholausschank. Hier solltest du selbst nachlesen oder eine Fatwa-Stelle bzw. einen Halal-Screener fragen.",
    ),
    "purification": Term(
        "Dividenden-Reinigung (Purification)", HALAL,
        "Den kleinen Anteil einer Dividende spenden, der aus nicht erlaubten Einnahmen stammt (z. B. Zinsen).",
        "Auch halal-konforme Firmen haben oft kleine Zinseinnahmen auf ihr Bankguthaben. Viele Anleger rechnen "
        "diesen Anteil heraus und spenden ihn.",
    ),
    "short_selling": Term(
        "Short-Selling & Hebel", HALAL,
        "Auf fallende Kurse wetten oder mit geliehenem Geld handeln – nach gängiger Auffassung nicht halal.",
        "Short-Selling bedeutet, geliehene Aktien zu verkaufen; Hebelprodukte (CFDs, Knock-outs) enthalten Kredit "
        "und Spekulation. „Verkaufen“ heißt in dieser App nur: die Aktie nicht (mehr) halten.",
    ),
    # ------------------------------------------------------------------ investor language
    "bullish_bearish": Term(
        "Bullish & Bearish", SLANG,
        "Bullish = man erwartet steigende Kurse, bearish = fallende.",
        "Merkhilfe: Der Bulle stößt mit den Hörnern nach oben, der Bär schlägt mit der Tatze nach unten. "
        "Ein „Bullenmarkt“ ist eine lange Aufwärtsphase, ein „Bärenmarkt“ ein Rückgang um mehr als 20 %.",
        "„Ich bin bullish auf SAP“ = „Ich glaube, SAP steigt.“",
    ),
    "buy_the_dip": Term(
        "Buy the Dip", SLANG,
        "Nach einem Kursrutsch („Dip“) nachkaufen, weil man auf Erholung setzt.",
        "Klappt nur, wenn der übergeordnete Trend intakt ist. Sonst „greift man in ein fallendes Messer“. "
        "Der Chart-Leser hilft: Liegt der Kurs noch über der 200-Tage-Linie?",
    ),
    "ath": Term(
        "ATH (All-Time High)", SLANG,
        "Allzeithoch – der höchste Kurs, den eine Aktie je hatte.",
        "Aktien auf einem Allzeithoch haben keinen Widerstand darüber; das gilt oft als Stärkezeichen.",
    ),
    "blue_chip": Term(
        "Blue Chip", SLANG,
        "Große, etablierte und bekannte Unternehmen wie Apple, SAP oder Nestlé.",
        "Blue Chips schwanken meist weniger als kleine Firmen und gelten als solidere Basis für ein Depot.",
    ),
    "penny_stock": Term(
        "Penny Stock", SLANG,
        "Sehr billige Aktien (unter 1 € bzw. 5 $), meist kleine und riskante Firmen.",
        "Wichtig: Ein niedriger Preis pro Aktie heißt nicht, dass die Aktie günstig ist. Ob sie günstig bewertet "
        "ist, zeigt z. B. das KGV. Bei vielen Brokern kannst du auch Bruchstücke teurer Aktien kaufen.",
    ),
    "fomo": Term(
        "FOMO (Fear of Missing Out)", SLANG,
        "Die Angst, einen Kursanstieg zu verpassen – verleitet zum Kaufen, wenn schon alle kaufen.",
        "FOMO-Käufe passieren oft kurz vor dem Hoch. Ein Warnzeichen: RSI über 70 (überkauft).",
    ),
    "hodl": Term(
        "HODL", SLANG,
        "Langfristig halten, auch wenn der Kurs wackelt.",
        "Entstanden aus einem Tippfehler von „hold“. Langfristig halten ist sinnvoll bei soliden Firmen – "
        "ein Stop-Loss schützt trotzdem vor großen Verlusten.",
    ),
    "portfolio": Term(
        "Portfolio / Depot", SLANG,
        "Alle Wertpapiere, die du besitzt. Das Depot ist das Konto dafür bei deinem Broker.",
        "Ein gutes Portfolio ist über mehrere Branchen und Länder verteilt (Diversifikation).",
    ),
    "diversifikation": Term(
        "Diversifikation", SLANG,
        "Dein Geld auf viele Aktien, Branchen und Länder verteilen.",
        "Wenn eine Aktie abstürzt, trifft es nicht dein ganzes Geld. „Nicht alle Eier in einen Korb legen.“",
    ),
    "etf": Term(
        "ETF", SLANG,
        "Ein Fonds, der einen ganzen Index nachbildet – viele Aktien auf einmal.",
        "Für Einsteiger oft der einfachste Start. Es gibt auch Islamic- bzw. Shariah-ETFs, die nur "
        "halal-konforme Aktien enthalten.",
    ),
    "sparplan": Term(
        "Sparplan", SLANG,
        "Regelmäßig einen festen Betrag investieren, z. B. 50 € im Monat.",
        "Du kaufst automatisch mal teurer, mal günstiger ein (Cost-Average-Effekt) und musst den perfekten "
        "Zeitpunkt nicht erraten.",
    ),
    "rendite": Term(
        "Rendite (Return)", SLANG,
        "Gewinn oder Verlust einer Geldanlage in Prozent.",
        "100 € werden zu 110 € → Rendite +10 %. Bei Aktien zählen Kursgewinne und Dividenden.",
    ),
    "rally_crash": Term(
        "Rally, Korrektur & Crash", SLANG,
        "Rally = starker Anstieg · Korrektur = Rückgang um ca. 10–20 % · Crash = schneller Einbruch über 20 %.",
        "Korrekturen sind normal und kommen etwa jedes Jahr vor. Wer sie kennt, gerät weniger in Panik.",
    ),
    "earnings": Term(
        "Earnings (Quartalszahlen)", SLANG,
        "Alle drei Monate veröffentlichen Firmen Umsatz und Gewinn – das bewegt den Kurs oft stark.",
        "„Beat“ = besser als erwartet, „Miss“ = schlechter. Auch der Ausblick („Guidance“) ist wichtig.",
    ),
    "broker": Term(
        "Broker / Neobroker", SLANG,
        "Der Anbieter, über den du Aktien kaufst – z. B. Trade Republic, Scalable Capital oder deine Bank.",
        "Chinesische und amerikanische Aktien handelst du dort meist über deutsche Börsen wie Tradegate oder "
        "Lang & Schwarz – in Euro.",
    ),
    "order": Term(
        "Market- vs. Limit-Order", SLANG,
        "Market-Order: sofort zum aktuellen Preis. Limit-Order: nur zu deinem Wunschpreis oder besser.",
        "Bei schwankenden Aktien schützt eine Limit-Order davor, zu teuer zu kaufen.",
    ),
}


def tip(key: str) -> str:
    """Short explanation for tooltips (help=...)."""
    return TERMS[key].short
