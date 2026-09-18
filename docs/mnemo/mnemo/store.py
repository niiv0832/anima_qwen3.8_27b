"""JSON persistence for cards."""

import json
import os
from typing import List

from .scheduler import Card


def load(path: str) -> List[Card]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Card(**c) for c in data]


def save(path: str, cards: List[Card]) -> None:
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([c.__dict__ for c in cards], f, ensure_ascii=False, indent=2)
