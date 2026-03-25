#!/bin/bash
set -euo pipefail

SETTINGS="$HOME/.claude/settings.json"

RED='\033[31m'
GREEN='\033[32m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { echo -e "${GREEN}▸${RESET} $1"; }
error() { echo -e "${RED}▸${RESET} $1"; exit 1; }

PACK="${1:-}"
[ -n "$PACK" ] || error "Usage: ./uninstall.sh <pack-name>"

# ── Remove verbs from settings.json ─────────────────────────────────────
if [ -f "$SETTINGS" ]; then
    python3 -c "
import json

settings_path = '$SETTINGS'
with open(settings_path) as f:
    settings = json.load(f)

settings.pop('spinnerVerbs', None)

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')
"
    info "Removed spinner verbs from $SETTINGS"
fi

# ── Remove alias from shell rc ──────────────────────────────────────────
MARKER="# vibescc:$PACK"
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if grep -q "$MARKER" "$rc" 2>/dev/null; then
        sed -i '' "/$MARKER/d" "$rc"
        info "Removed alias from $rc"
    fi
done

echo ""
echo -e "${GREEN}${BOLD}Done!${RESET} ${BOLD}$PACK${RESET} alias removed. Verbs back to defaults on next launch."
