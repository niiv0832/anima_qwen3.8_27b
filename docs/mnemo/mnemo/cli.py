"""Command-line interface for mnemo."""

import argparse
import datetime
import os

from .scheduler import Card, schedule, is_due
from .store import load, save

DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".mnemo", "cards.json")


def _today() -> str:
    return datetime.date.today().isoformat()


def cmd_add(args):
    cards = load(args.db)
    cards.append(Card(front=args.front, back=args.back, due=_today()))
    save(args.db, cards)
    print(f"Добавлено. Всего карт: {len(cards)}")


def cmd_list(args):
    cards = load(args.db)
    if not cards:
        print("Нет карт.")
        return
    for i, c in enumerate(cards, 1):
        print(f"{i}. {c.front}  →  {c.back}  (due {c.due}, EF {c.ease:.2f}, int {c.interval:.0f}d)")


def cmd_review(args):
    today = _today()
    cards = load(args.db)
    due = [c for c in cards if is_due(c, today)]
    if not due:
        print("Нет карт для повторения сегодня.")
        return
    print(f"Карт на сегодня: {len(due)}\n")
    for c in due:
        print(f"Вопрос: {c.front}")
        try:
            input("  (нажми Enter, когда вспомнишь ответ) ")
        except EOFError:
            break
        print(f"Ответ: {c.back}\n")
        print("  Оценка: 0-2 (не вспомнил) / 3 (трудно) / 4 (норм) / 5 (легко)")
        try:
            q = int(input("  > "))
        except (EOFError, ValueError):
            q = 3
        idx = cards.index(c)
        cards[idx] = schedule(c, q, today)
        save(args.db, cards)
        print(f"  → следующее повторение: {cards[idx].due}\n")


def cmd_stats(args):
    today = _today()
    cards = load(args.db)
    if not cards:
        print("Нет карт.")
        return
    due = sum(1 for c in cards if is_due(c, today))
    print(f"Всего карт: {len(cards)}")
    print(f"На сегодня: {due}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mnemo", description="Минимальный spaced repetition.")
    parser.add_argument("--db", default=DEFAULT_DB, help="путь к файлу карт")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="добавить карту")
    p_add.add_argument("front")
    p_add.add_argument("back")
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="показать все карты")
    p_list.set_defaults(func=cmd_list)

    p_review = sub.add_parser("review", help="повторить карты")
    p_review.set_defaults(func=cmd_review)

    p_stats = sub.add_parser("stats", help="статистика")
    p_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
