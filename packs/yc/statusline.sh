#!/bin/bash
set -euo pipefail

# VibesCC Statusline — Y Combinator Brand Pack
# Multi-line output: crab sprite + status info

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

# Colors
O="\033[38;2;255;102;0m"  # YC orange
W="\033[37m"               # white
G="\033[90m"               # gray
R="\033[0m"                # reset
B="\033[1m"                # bold

# Context color
CTX=""
if [ -n "$CONTEXT_PCT" ]; then
  CTX_INT=${CONTEXT_PCT%.*}
  if [ "$CTX_INT" -lt 40 ]; then
    CC="\033[32m"
  elif [ "$CTX_INT" -lt 70 ]; then
    CC="\033[33m"
  else
    CC="\033[31m"
  fi
  CTX="${CC}${CTX_INT}%${R}"
else
  CTX="${G}--${R}"
fi

# Status line
STATUS="${O}${B}YC${R}"
if [ -n "$BRANCH" ]; then
  STATUS="${STATUS} ${G}│${R} ${W}${BRANCH}${R}"
fi
STATUS="${STATUS} ${G}│${R} ctx ${CTX}"

# YC Crab — 6 lines, ~18 chars wide
# Uses half-block Unicode chars for pixel density
# The crab has a YC shield on its body
echo -e "   ${O}▐${W}▄▄▄▄${O}▌${R}"
echo -e "   ${O}▐${W}${B} YC ${R}${O}▌${R}"
echo -e "  ${O}▄▟${W}▀▀▀▀${O}▙▄${R}"
echo -e " ${O}▞▚${R}${O}◉${R}${W}▄▄▄▄${R}${O}◉${R}${O}▞▚${R}"
echo -e " ${O}▚▞ ${R}${O}▀▄▄▀${R}${O} ▚▞${R}"
echo -e " ${O}╱╲${R}        ${O}╱╲${R}"
echo -e " ${STATUS}"
