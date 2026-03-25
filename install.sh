#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PACKS_DIR="$SCRIPT_DIR/packs"
LAUNCHER="$SCRIPT_DIR/scripts/vibescc-launch.py"
SETTINGS="$HOME/.claude/settings.json"

# ── Colors ──────────────────────────────────────────────────────────────
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BOLD='\033[1m'
RESET='\033[0m'

info()  { echo -e "${GREEN}▸${RESET} $1"; }
warn()  { echo -e "${YELLOW}▸${RESET} $1"; }
error() { echo -e "${RED}▸${RESET} $1"; exit 1; }

# ── Pick pack ───────────────────────────────────────────────────────────
PACK="${1:-}"

if [ -z "$PACK" ]; then
    echo -e "${BOLD}Available packs:${RESET}"
    echo ""
    for dir in "$PACKS_DIR"/*/; do
        slug=$(basename "$dir")
        name=$(python3 -c "import json; print(json.load(open('$dir/pack.json'))['name'])")
        body=$(python3 -c "import json; print(json.load(open('$dir/pack.json'))['colors']['body'])")
        echo "  $slug  ($name, $body)"
    done
    echo ""
    read -p "Pick a pack: " PACK
fi

PACK_DIR="$PACKS_DIR/$PACK"
[ -d "$PACK_DIR" ] || error "Pack '$PACK' not found in $PACKS_DIR"

PACK_JSON="$PACK_DIR/pack.json"
PACK_NAME=$(python3 -c "import json; print(json.load(open('$PACK_JSON'))['name'])")

info "Installing ${BOLD}$PACK_NAME${RESET} pack"

# ── Install verbs to ~/.claude/settings.json ────────────────────────────
info "Writing spinner verbs to $SETTINGS"

python3 -c "
import json, sys

pack = json.load(open('$PACK_JSON'))
verbs = pack['verbs']

settings_path = '$SETTINGS'
try:
    with open(settings_path) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

settings['spinnerVerbs'] = {
    'mode': 'replace',
    'verbs': verbs
}

# Clean up old statusline if vibescc left one
if settings.get('statusLine', {}).get('command', '').endswith('vibescc-statusline.sh'):
    del settings['statusLine']

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')

print(f'  {len(verbs)} verbs installed')
"

# ── Add shell alias ─────────────────────────────────────────────────────
SHELL_RC="$HOME/.zshrc"
if [ -n "${BASH_VERSION:-}" ] || [ ! -f "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

ALIAS_LINE="alias $PACK='python3 $LAUNCHER --config $PACK_DIR'"
MARKER="# vibescc:$PACK"

if grep -q "$MARKER" "$SHELL_RC" 2>/dev/null; then
    # Update existing alias
    sed -i '' "/$MARKER/d" "$SHELL_RC"
fi

echo "$ALIAS_LINE $MARKER" >> "$SHELL_RC"
info "Added alias ${BOLD}$PACK${RESET} to $SHELL_RC"

# ── Done ────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}Done!${RESET} Open a new terminal and type ${BOLD}$PACK${RESET} to launch."
echo -e "All claude flags work: ${BOLD}$PACK --resume${RESET}, ${BOLD}$PACK --dangerously-skip-permissions${RESET}, etc."
echo ""
echo -e "To uninstall: ${BOLD}./uninstall.sh $PACK${RESET}"
