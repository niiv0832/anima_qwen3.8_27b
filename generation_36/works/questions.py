#!/usr/bin/env python3
"""Извлекает вопросы из всех поколений.

Вопрос = строка, содержащая '?', длина > 15 символов,
не URL, не код, не комментарий.
"""

import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(BASE)  # anima_qwen3.8_27b/

SKIP_FILES = {"AGENTS.md", "INBOX.md", "MAIN_GOAL.md", "loop.sh", "run.sh"}

def is_question(line: str) -> bool:
    line = line.strip()
    if len(line) < 15:
        return False
    if "?" not in line:
        return False
    if line.startswith(("http", "```", "#", "//", "/*")):
        return False
    if re.match(r"^\s*[\w\-]+\s*[:=]\s*", line):
        return False
    return True

def main():
    results = []
    for gen in sorted(os.listdir(BASE), key=lambda x: int(x.split("_")[1]) if x.startswith("generation_") and x.split("_")[1].isdigit() else 999):
        if not gen.startswith("generation_"):
            continue
        gen_dir = os.path.join(BASE, gen)
        if not os.path.isdir(gen_dir):
            continue
        for fname in os.listdir(gen_dir):
            if fname in SKIP_FILES:
                continue
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(gen_dir, fname)
            if not os.path.isfile(fpath):
                continue
            with open(fpath, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if is_question(line):
                        results.append((gen, fname, i, line.strip()))

    for gen, fname, line_no, text in results:
        print(f"{gen}/{fname}:{line_no}  {text}")

if __name__ == "__main__":
    main()
