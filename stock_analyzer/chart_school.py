"""Chart school: short lessons on how to read charts, with illustrative example data."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Lesson:
    key: str
    icon: str
    title: str
    intro: str
    how: list[str]
    up: list[str] = field(default_factory=list)
    down: list[str] = field(default_factory=list)


LESSONS: list[Lesson] = [
    Lesson(
        "grundlagen", "📈", "Einen Kurschart lesen",
        "Ein Kurschart zeigt, wie sich der Preis einer Aktie über die Zeit verändert hat.",
        [
            "Waagerechte Achse: die Zeit – links liegt die Vergangenheit, ganz rechts ist heute.",
            "Senkrechte Achse: der Kurs in Euro oder Dollar.",
            "Jeder Punkt der Linie ist der Schlusskurs eines Handelstages.",
            "Hochs sind Spitzen, an denen der Kurs nach unten gedreht hat; Tiefs sind Täler, an denen er wieder "
            "gestiegen ist.",
            "Wichtig ist nicht jeder Zacken, sondern die grobe Richtung über Wochen und Monate.",
        ],
    ),
    Lesson(
        "trend", "↗️", "Trends erkennen",
        "Kurse bewegen sich in Wellen. Entscheidend ist, ob die Wellen immer höher oder immer tiefer werden – "
        "ein bestehender Trend setzt sich statistisch eher fort, als dass er plötzlich endet.",
        [
            "Aufwärtstrend: Jedes Hoch liegt höher als das vorige, jedes Tief ebenfalls (höhere Hochs, höhere Tiefs).",
            "Abwärtstrend: tiefere Hochs und tiefere Tiefs.",
            "Seitwärtstrend: Hochs und Tiefs liegen ungefähr auf gleicher Höhe – der Markt ist unentschlossen.",
            "Ein Trend gilt als gebrochen, wenn das Muster reißt, z. B. wenn im Aufwärtstrend ein Tief unter das "
            "letzte Tief fällt.",
        ],
        up=["Höhere Hochs und höhere Tiefs", "Rücksetzer enden über dem letzten Tief"],
        down=["Tiefere Hochs und tiefere Tiefs", "Erholungen scheitern unter dem letzten Hoch"],
    ),
    Lesson(
        "durchschnitte", "〰️", "50- und 200-Tage-Linie, Golden & Death Cross",
        "Gleitende Durchschnitte glätten das tägliche Zickzack. Die 50-Tage-Linie zeigt den mittelfristigen, "
        "die 200-Tage-Linie den langfristigen Trend.",
        [
            "In dieser App: blau = Kurs, orange = 50-Tage-Linie, grün = 200-Tage-Linie.",
            "Liegt der Kurs über einer Linie, haben die Käufer in diesem Zeitraum die Oberhand.",
            "Die Linien wirken oft wie ein Boden (im Aufwärtstrend) oder eine Decke (im Abwärtstrend).",
            "Golden Cross: Die 50-Tage-Linie kreuzt die 200-Tage-Linie von unten nach oben. Death Cross: umgekehrt.",
        ],
        up=["Kurs über der 200-Tage-Linie", "Golden Cross", "Beide Linien zeigen nach oben",
            "Kurs prallt von der 50-Tage-Linie nach oben ab"],
        down=["Kurs unter der 200-Tage-Linie", "Death Cross", "Kurs durchbricht die 50-Tage-Linie nach unten"],
    ),
    Lesson(
        "unterstuetzung", "🧱", "Unterstützung, Widerstand & Ausbruch",
        "Manche Kursniveaus wirken wie Boden und Decke, weil dort früher viele Anleger gekauft oder verkauft haben.",
        [
            "Unterstützung (Boden): ein Kurs, an dem die Aktie mehrfach wieder nach oben gedreht hat.",
            "Widerstand (Decke): ein Kurs, an dem sie mehrfach nach unten abgeprallt ist.",
            "Ausbruch: Der Kurs schließt klar über dem Widerstand – häufig startet dann eine neue Aufwärtsbewegung.",
            "Aus einem durchbrochenen Widerstand wird oft eine neue Unterstützung (und umgekehrt).",
        ],
        up=["Ausbruch über einen Widerstand", "Abprall an einer Unterstützung", "Neues 3-Monats- oder Jahreshoch"],
        down=["Bruch einer Unterstützung", "Mehrfaches Scheitern am Widerstand", "Neues 3-Monats-Tief"],
    ),
    Lesson(
        "volumen", "📊", "Volumen: Wie viele machen mit?",
        "Das Volumen zeigt, wie viele Aktien an einem Tag gehandelt wurden. Es verrät, wie überzeugt die Anleger sind.",
        [
            "Die Balken unter dem Kurs zeigen das Volumen – je höher, desto mehr wurde gehandelt.",
            "Grüne Balken: Tage mit Kursgewinn, rote Balken: Tage mit Kursverlust.",
            "Steigt der Kurs bei hohem Volumen, kaufen viele mit – die Bewegung gilt als „bestätigt“.",
            "Steigt der Kurs bei immer weniger Volumen, fehlt die Überzeugung.",
        ],
        up=["Kursanstieg mit steigendem Volumen", "Ausbruch mit besonders hohem Volumen"],
        down=["Kursrückgang mit hohem Volumen (Verkaufsdruck)", "Anstieg bei immer weniger Volumen"],
    ),
    Lesson(
        "rsi", "🌡️", "RSI: überhitzt oder unterkühlt?",
        "Der RSI misst auf einer Skala von 0 bis 100, wie stark die Gewinne der letzten 14 Tage die Verluste "
        "überwiegen – wie ein Thermometer für die Aktie.",
        [
            "Über 70: überkauft – die Aktie ist sehr schnell gestiegen, eine Verschnaufpause wird wahrscheinlicher.",
            "Unter 30: überverkauft – nach starkem Fall ist eine Gegenbewegung möglich.",
            "Zwischen 50 und 70: gesunde Stärke im Aufwärtstrend.",
            "In starken Trends kann der RSI lange überkauft bleiben – er ist ein Warnlicht, kein Verkaufsbefehl.",
        ],
        up=["RSI steigt aus dem Bereich unter 30 wieder heraus", "RSI hält sich im Aufwärtstrend über 50"],
        down=["RSI fällt aus dem Bereich über 70 zurück",
              "Kurs macht ein neues Hoch, der RSI aber nicht (Divergenz – der Schwung lässt nach)"],
    ),
    Lesson(
        "macd", "⚡", "MACD: Nimmt der Schwung zu?",
        "Der MACD vergleicht einen schnellen mit einem langsamen Durchschnitt und zeigt, ob eine Bewegung an "
        "Fahrt gewinnt oder verliert.",
        [
            "Zwei Linien: die MACD-Linie (blau) und ihre Signallinie (orange).",
            "Die Balken zeigen den Abstand zwischen beiden – wachsende Balken = zunehmender Schwung.",
            "Kreuzt die MACD-Linie die Signallinie nach oben, nimmt der Aufwärtsschwung zu; nach unten lässt er nach.",
        ],
        up=["MACD kreuzt die Signallinie nach oben", "MACD steigt über die Nulllinie"],
        down=["MACD kreuzt die Signallinie nach unten", "MACD fällt unter die Nulllinie"],
    ),
    Lesson(
        "app", "🧭", "Die Diagramme dieser App",
        "So liest du die Diagramme im Tab „Aktie analysieren“.",
        [
            "<b>Kursverlauf und Prognose:</b> blau der Kurs, orange die 50-Tage-, grün die 200-Tage-Linie. "
            "Die grün gestrichelte Linie ist das Kursziel, die rote der Stop-Loss. Die gepunktete senkrechte Linie "
            "markiert das Datum „Verkauf ab“ bzw. „Halten bis“.",
            "<b>Chart-Leser:</b> Nummerierte Punkte markieren erkannte Zeichen (z. B. ein Golden Cross), die "
            "gepunkteten Linien die nächste Unterstützung (grün) und den nächsten Widerstand (rot).",
            "<b>Die sieben Faktoren:</b> Balken nach rechts (blau) sprechen für die Aktie, Balken nach links (rot) "
            "dagegen. Je länger, desto stärker.",
            "<b>Verlauf des Signal-Scores:</b> Die Linie ist die Gesamtnote. Die farbigen Zonen entsprechen den "
            "fünf Empfehlungen – liegt die Linie in der grünen Zone, stand die Aktie auf Kaufen.",
            "<b>Volumen, RSI & MACD:</b> die Werkzeuge aus den Lektionen oben, für die gewählte Aktie.",
        ],
    ),
]

SHORT = {
    "grundlagen": "Grundlagen", "trend": "Trends", "durchschnitte": "50/200-Tage-Linie",
    "unterstuetzung": "Unterstützung & Ausbruch", "volumen": "Volumen", "rsi": "RSI", "macd": "MACD",
    "app": "Charts dieser App",
}

CHECKLIST_UP = [
    "Höhere Hochs und höhere Tiefs",
    "Kurs über der 50- und 200-Tage-Linie",
    "Golden Cross",
    "Ausbruch über einen Widerstand",
    "Anstieg mit hohem Volumen",
    "RSI zwischen 50 und 70 oder aus „überverkauft“ kommend",
    "MACD kreuzt die Signallinie nach oben",
]
CHECKLIST_DOWN = [
    "Tiefere Hochs und tiefere Tiefs",
    "Kurs unter der 50- und 200-Tage-Linie",
    "Death Cross",
    "Bruch einer Unterstützung",
    "Kursrückgang mit hohem Volumen",
    "RSI fällt aus „überkauft“ zurück oder Divergenz",
    "MACD kreuzt die Signallinie nach unten",
]


# ---------------------------------------------------------------------------- example data

def _path(anchors: list[float], days: int, noise: float = 0.006, seed: int = 0) -> pd.Series:
    """Piecewise-linear path through the anchor prices with small daily noise."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, len(anchors) - 1, days)
    base = np.interp(x, np.arange(len(anchors)), anchors)
    wiggle = np.cumsum(rng.normal(0, noise, days))
    wiggle -= np.linspace(wiggle[0], wiggle[-1], days)  # keep the anchors' start and end
    index = pd.bdate_range(end="2026-06-30", periods=days)
    return pd.Series(base * np.exp(wiggle), index=index)


def example(key: str) -> dict[str, pd.Series]:
    """Illustrative price series for a lesson (deterministic)."""
    if key == "grundlagen":
        return {"close": _path([100, 114, 106, 122, 112, 131], 130, seed=1)}
    if key == "trend":
        return {
            "Aufwärtstrend": _path([100, 110, 104, 116, 109, 123, 116, 130], 120, 0.004, seed=2),
            "Seitwärtstrend": _path([100, 108, 99, 107, 100, 108, 99, 106], 120, 0.004, seed=3),
            "Abwärtstrend": _path([130, 120, 126, 114, 120, 108, 113, 100], 120, 0.004, seed=4),
        }
    if key == "durchschnitte":
        return {"close": _path([120, 112, 100, 92, 96, 104, 112, 124, 132, 140], 420, 0.008, seed=5)}
    if key == "unterstuetzung":
        return {"close": _path([96, 104.5, 95.5, 104.8, 95.2, 104.6, 96, 104.4, 112, 118], 200, 0.004, seed=6)}
    if key == "volumen":
        close = _path([100, 103, 101, 106, 104, 108, 118, 124], 160, 0.004, seed=7)
        rng = np.random.default_rng(8)
        change = close.pct_change().fillna(0)
        volume = 1e6 * (1 + 25 * change.abs()) * rng.lognormal(0, 0.2, len(close))
        volume.iloc[-60:-40] *= 2.2  # breakout on heavy volume
        return {"close": close, "volume": volume}
    if key == "rsi":
        return {"close": _path([100, 104, 118, 131, 124, 110, 97, 92, 99, 108], 200, 0.006, seed=9)}
    if key == "macd":
        return {"close": _path([100, 94, 90, 97, 108, 115, 111, 104, 99, 106, 114], 220, 0.006, seed=10)}
    return {}
