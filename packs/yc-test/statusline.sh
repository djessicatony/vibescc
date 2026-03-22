#!/bin/bash
set -euo pipefail

# VibesCC Statusline — yc-test Brand Pack
INPUT=$(cat)

extract_json() {
  local key="$1"
  echo "$INPUT" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*[^,}]*" | head -1 | sed 's/.*:[[:space:]]*//' | tr -d '"'
}

extract_nested() {
  local key="$1"
  echo "$INPUT" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*[0-9.]*" | head -1 | sed 's/.*:[[:space:]]*//' | tr -d '"'
}

CURRENT_DIR=$(extract_json "current_dir")
CONTEXT_PCT=$(extract_nested "used_percentage")

BRANCH=""
if git -C "$CURRENT_DIR" rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null || echo "")
fi

BRAND="\033[38;2;215;119;87m"
GRAY="\033[90m"
RESET="\033[0m"
BOLD="\033[1m"

if [ -n "$CONTEXT_PCT" ]; then
  CTX_INT=${CONTEXT_PCT%.*}
  if [ "$CTX_INT" -lt 40 ]; then
    CTX_COLOR="\033[32m"
  elif [ "$CTX_INT" -lt 70 ]; then
    CTX_COLOR="\033[33m"
  else
    CTX_COLOR="\033[31m"
  fi
  CTX_DISPLAY="${CTX_COLOR}${CTX_INT}%${RESET}"
else
  CTX_DISPLAY="${GRAY}--${RESET}"
fi

OUTPUT="${BRAND}${BOLD}YC-TEST${RESET}"

if [ -n "$BRANCH" ]; then
  OUTPUT="${OUTPUT} ${GRAY}|${RESET} ${BRANCH}"
fi

OUTPUT="${OUTPUT} ${GRAY}|${RESET} ctx ${CTX_DISPLAY}"

echo -e "$OUTPUT"
