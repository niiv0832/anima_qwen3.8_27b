#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MAIN_GOAL_FILE="$SCRIPT_DIR/MAIN_GOAL.md"
MODEL="${ANIMA_MODEL:-}"
THINKING="${ANIMA_THINKING:-1}"

main_goal="$(<"$MAIN_GOAL_FILE")"

(
  cd "$SCRIPT_DIR"

  args=(--auto)
  if [[ -n "$MODEL" ]]; then
    args+=(-m "$MODEL")
  fi
  if [[ "$THINKING" == "1" ]]; then
    args+=(--thinking)
  fi

  opencode run "${args[@]}" "$main_goal"
)
