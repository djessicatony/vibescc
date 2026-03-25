#!/bin/bash
set -euo pipefail

SETTINGS="$HOME/.claude/settings.json"

GREEN='\033[32m'
BOLD='\033[1m'
RESET='\033[0m'

info() { echo -e "${GREEN}▸${RESET} $1"; }

# ── Remove verbs from settings.json ─────────────────────────────────────
if [ -f "$SETTINGS" ]; then
    python3 -c "
import json
with open('$SETTINGS') as f:
    settings = json.load(f)
settings.pop('spinnerVerbs', None)
with open('$SETTINGS', 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')
"
    info "Removed spinner verbs"
fi

# ── Remove all vibescc aliases from shell rc ─────────────────────────────
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if grep -q "# vibescc:" "$rc" 2>/dev/null; then
        sed -i '' '/# vibescc:/d' "$rc"
        info "Removed aliases from $rc"
    fi
done

echo ""
echo -e "${GREEN}${BOLD}Done!${RESET} All vibescc aliases and verbs removed."
