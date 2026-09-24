"""Learning helpers: a daily term and a small multiple-choice quiz built from the glossary."""
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date

from .glossary import APP, HALAL, INDIKATOR, KENNZAHL, RISIKO, SLANG, TERMS

# Terms that make good daily words and quiz questions.
_POOL_CATEGORIES = (SLANG, HALAL, KENNZAHL, RISIKO, INDIKATOR, APP)
POOL = [key for key, term in TERMS.items() if term.category in _POOL_CATEGORIES]
_DAILY = [key for key, term in TERMS.items() if term.category in (SLANG, HALAL, KENNZAHL, RISIKO)]


def word_of_the_day(day: date | None = None) -> str:
    day = day or date.today()
    return _DAILY[day.toordinal() % len(_DAILY)]


@dataclass(frozen=True)
class Question:
    key: str
    prompt: str
    options: tuple[str, ...]
    answer: int  # index into options


def quiz(seed: int, n: int = 5, choices: int = 3) -> list[Question]:
    """`n` questions "What does X mean?" with one correct and two wrong explanations."""
    rng = random.Random(seed)
    keys = rng.sample(POOL, n)
    questions = []
    for key in keys:
        wrong = rng.sample([k for k in POOL if k != key and TERMS[k].short != TERMS[key].short], choices - 1)
        options = [TERMS[key].short] + [TERMS[k].short for k in wrong]
        rng.shuffle(options)
        questions.append(Question(key, f"Was bedeutet „{TERMS[key].title}“?", tuple(options),
                                  options.index(TERMS[key].short)))
    return questions
