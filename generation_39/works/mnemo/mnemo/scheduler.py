"""SM-2 spaced repetition scheduler.

Pure functions. No I/O. Easy to test.
"""

import datetime
from dataclasses import dataclass


@dataclass
class Card:
    front: str
    back: str
    ease: float = 2.5
    interval: float = 0.0
    reps: int = 0
    due: str = ""


def schedule(card: Card, quality: int, today: str) -> Card:
    """Apply one SM-2 review. quality in 0..5, today is ISO date.

    Returns a new Card (does not mutate the input).
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality must be 0..5")

    q = quality
    ef = card.ease
    reps = card.reps
    interval = card.interval

    if q < 3:
        reps = 0
        interval = 1.0
    else:
        if reps == 0:
            interval = 1.0
        elif reps == 1:
            interval = 6.0
        else:
            interval = round(interval * ef, 1)
        ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if ef < 1.3:
            ef = 1.3
        reps += 1

    due_date = datetime.date.fromisoformat(today) + datetime.timedelta(days=int(interval))
    due = due_date.isoformat()

    return Card(
        front=card.front,
        back=card.back,
        ease=round(ef, 4),
        interval=round(interval, 1),
        reps=reps,
        due=due,
    )


def is_due(card: Card, today: str) -> bool:
    return card.due <= today
