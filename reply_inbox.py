#!/usr/bin/env python3
"""Агент отвечает на INBOX-issue.

Использование:
    python3 reply_inbox.py "текст ответа"

Ответ публикуется как комментарий к issue #1.
"""

import json
import os
import subprocess
import sys
import urllib.request

REPO = "niiv0832/anima_qwen3.8_27b"
INBOX_ISSUE_NUMBER = 1


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


def main():
    if len(sys.argv) < 2:
        print("Usage: reply_inbox.py \"message\"", file=sys.stderr)
        sys.exit(1)

    message = sys.argv[1]
    token = get_token()
    if not token:
        print("reply_inbox: нет токена GitHub", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.github.com/repos/{REPO}/issues/{INBOX_ISSUE_NUMBER}/comments"
    data = json.dumps({"body": message}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "anima-reply-inbox",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            print(f"reply_inbox: ответ опубликован: {result.get('html_url', '')}")
    except Exception as e:
        print(f"reply_inbox: ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
