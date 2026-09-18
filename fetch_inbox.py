#!/usr/bin/env python3
"""Подтягивает новые комментарии из INBOX-issue в INBOX.md.

Использование:
    python3 fetch_inbox.py <path_to_INBOX.md>

Состояние (последний прочитанный comment id) хранится в inbox_state.json
рядом со скриптом. Скрипт идемпотентен: повторный запуск не дублирует
сообщения.
"""

import json
import os
import subprocess
import sys
import urllib.request

REPO = "niiv0832/anima_qwen3.8_27b"
INBOX_ISSUE_NUMBER = 1
AGENT_LOGIN = "niiv0832"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "inbox_state.json")


def get_token():
    try:
        result = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("password="):
            return line.split("=", 1)[1]
    return None


def api_get(url, token):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "anima-fetch-inbox",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_comment_id": 0}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_inbox.py <path_to_INBOX.md>", file=sys.stderr)
        sys.exit(1)

    inbox_path = sys.argv[1]
    token = get_token()
    if not token:
        print("fetch_inbox: нет токена GitHub, пропускаю", file=sys.stderr)
        return

    state = load_state()
    last_id = state.get("last_comment_id", 0)

    try:
        comments = api_get(
            f"https://api.github.com/repos/{REPO}/issues/{INBOX_ISSUE_NUMBER}/comments?per_page=100",
            token,
        )
    except Exception as e:
        print(f"fetch_inbox: ошибка API: {e}", file=sys.stderr)
        return

    new_comments = [
        c for c in comments
        if c["id"] > last_id
        and c.get("user", {}).get("login") != AGENT_LOGIN
    ]
    if not new_comments:
        print("fetch_inbox: новых сообщений нет")
        return

    with open(inbox_path, "a", encoding="utf-8") as f:
        f.write("\n---\n\n# Входящие (GitHub issue #1)\n\n")
        for c in new_comments:
            login = c.get("user", {}).get("login", "unknown")
            created = c.get("created_at", "")
            f.write(f"\n## Сообщение от {login} ({created})\n\n")
            f.write(c.get("body", "").strip() + "\n")

    state["last_comment_id"] = max(c["id"] for c in new_comments)
    save_state(state)
    print(f"fetch_inbox: получено {len(new_comments)} нов. сообщ.")


if __name__ == "__main__":
    main()
