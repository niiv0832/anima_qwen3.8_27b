#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

find_latest_generation() {
  local max_num=-1
  local latest=""

  shopt -s nullglob
  for path in "$SCRIPT_DIR"/generation_*; do
    [[ -d "$path" ]] || continue
    local base num
    base="$(basename "$path")"
    num="${base#generation_}"
    [[ "$num" =~ ^[0-9]+$ ]] || continue
    if (( num > max_num )); then
      max_num="$num"
      latest="$path"
    fi
  done
  shopt -u nullglob

  echo "$latest"
}

next_generation_number() {
  local max_num=0

  shopt -s nullglob
  for path in "$SCRIPT_DIR"/generation_*; do
    [[ -d "$path" ]] || continue
    local base num
    base="$(basename "$path")"
    num="${base#generation_}"
    [[ "$num" =~ ^[0-9]+$ ]] || continue
    if (( num > max_num )); then
      max_num="$num"
    fi
  done
  shopt -u nullglob

  echo "$((max_num + 1))"
}

create_new_generation() {
  local next_num
  next_num="$(next_generation_number)"
  local new_dir="$SCRIPT_DIR/generation_$next_num"

  local prev_dir
  prev_dir="$(find_latest_generation)"

  echo "=== Создаю generation_$next_num ===" >&2
  mkdir -p "$new_dir"

  for file in MAIN_GOAL.md AGENTS.md loop.sh run.sh; do
    if [[ -f "$SCRIPT_DIR/$file" ]]; then
      cp "$SCRIPT_DIR/$file" "$new_dir/$file"
    fi
  done

  chmod +x "$new_dir/loop.sh" "$new_dir/run.sh" 2>/dev/null || true

  # Форматтер живёт в корне (стабильный инструмент).
  # Ищем самый свежий handoff.json в предыдущих генерациях (от свежей к старой).
  local prepare_script="$SCRIPT_DIR/prepare_inbox.py"
  local found_handoff=""
  local max_num
  max_num="$(next_generation_number)"
  local i=$((max_num - 1))
  while (( i >= 1 )); do
    local candidate="$SCRIPT_DIR/generation_$i/works/handoff.json"
    if [[ -f "$candidate" ]]; then
      found_handoff="$candidate"
      break
    fi
    i=$((i - 1))
  done

  if [[ -n "$found_handoff" && -f "$prepare_script" ]]; then
    echo "=== Передаю handoff из $(basename "$(dirname "$(dirname "$found_handoff")")") ===" >&2
    python3 "$prepare_script" "$found_handoff" > "$new_dir/INBOX.md" 2>/dev/null || : > "$new_dir/INBOX.md"
  else
    : > "$new_dir/INBOX.md"
  fi

  # Подтянуть реальные сообщения из GitHub INBOX-issue
  local fetch_script="$SCRIPT_DIR/fetch_inbox.py"
  if [[ -f "$fetch_script" ]]; then
    echo "=== Подтягиваю входящие из GitHub ===" >&2
    python3 "$fetch_script" "$new_dir/INBOX.md" 2>/dev/null || true
  fi

  echo "$new_dir"
}

run_generation() {
  local dir="$1"

  echo "=== Запуск поколения: $(basename "$dir") ==="
  (
    cd "$dir"
    ANIMA_META_LOOP=1 bash "./loop.sh"
  )
  echo "=== Поколение завершилось: $(basename "$dir") ==="
}

# --- Главный цикл ---

while true; do
  latest="$(find_latest_generation)"

  if [[ -z "$latest" ]]; then
    echo "=== Нет ни одной generation_*, создаю первую ==="
    latest="$(create_new_generation)"
  fi

  if [[ -f "$latest/STOP" ]]; then
    echo "=== $(basename "$latest") остановлена (STOP), создаю следующую ==="
    latest="$(create_new_generation)"
  fi

  if [[ ! -f "$latest/loop.sh" ]]; then
    echo "В $(basename "$latest") нет loop.sh, невозможно запустить" >&2
    exit 1
  fi

  run_generation "$latest"

  if [[ ! -f "$latest/STOP" ]]; then
    echo "=== loop.sh завершился без STOP — аварийная остановка ===" >&2
    exit 1
  fi
done
