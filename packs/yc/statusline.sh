#!/bin/bash
set -euo pipefail

# VibesCC Statusline — Y Combinator Brand Pack
# Reads session JSON from stdin, outputs branded statusline

# Read JSON input from Claude Code
INPUT=$(cat)

# Parse fields (using built-in string manipulation to avoid jq dependency)
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

# Get git branch if in a repo
BRANCH=""
if git -C "$CURRENT_DIR" rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null || echo "")
fi

# YC brand colors
YC_ORANGE="\033[38;2;255;102;0m"
WHITE="\033[37m"
GRAY="\033[90m"
RESET="\033[0m"
BOLD="\033[1m"

# Context color (green → yellow → red)
if [ -n "$CONTEXT_PCT" ]; then
  CTX_INT=${CONTEXT_PCT%.*}
  if [ "$CTX_INT" -lt 40 ]; then
    CTX_COLOR="\033[32m"  # green
  elif [ "$CTX_INT" -lt 70 ]; then
    CTX_COLOR="\033[33m"  # yellow
  else
    CTX_COLOR="\033[31m"  # red
  fi
  CTX_DISPLAY="${CTX_COLOR}${CTX_INT}%${RESET}"
else
  CTX_DISPLAY="${GRAY}--${RESET}"
fi

# YC Crab mascot (compact for statusline)
CRAB="${YC_ORANGE}╱▔╲${RESET}"

# Build output
OUTPUT="${CRAB} ${YC_ORANGE}${BOLD}YC${RESET}"

if [ -n "$BRANCH" ]; then
  OUTPUT="${OUTPUT} ${GRAY}│${RESET} ${WHITE}${BRANCH}${RESET}"
fi

OUTPUT="${OUTPUT} ${GRAY}│${RESET} ctx ${CTX_DISPLAY}"

echo -e "$OUTPUT"
