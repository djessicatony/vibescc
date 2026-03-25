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
DIM='\033[2m'
RESET='\033[0m'

info()  { echo -e "${GREEN}▸${RESET} $1"; }
warn()  { echo -e "${YELLOW}▸${RESET} $1"; }
error() { echo -e "${RED}▸${RESET} $1"; exit 1; }

# ── Detect shell rc ─────────────────────────────────────────────────────
# Default to zsh on macOS, bash elsewhere. Create the file if missing.
if [ "$(basename "$SHELL")" = "zsh" ] || [ "$(uname)" = "Darwin" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi
touch "$SHELL_RC"

# ── Collect available packs ─────────────────────────────────────────────
SLUGS=()
NAMES=()
BODIES=()
for dir in "$PACKS_DIR"/*/; do
    slug=$(basename "$dir")
    name=$(python3 -c "import json; print(json.load(open('$dir/pack.json'))['name'])")
    body=$(python3 -c "import json; print(json.load(open('$dir/pack.json'))['colors']['body'])")
    SLUGS+=("$slug")
    NAMES+=("$name")
    BODIES+=("$body")
done

# ── Install a single pack (alias + verbs) ───────────────────────────────
install_pack() {
    local slug="$1"
    local pack_dir="$PACKS_DIR/$slug"
    local pack_json="$pack_dir/pack.json"
    local pack_name
    pack_name=$(python3 -c "import json; print(json.load(open('$pack_json'))['name'])")

    # Write verbs
    python3 -c "
import json

pack = json.load(open('$pack_json'))
verbs = pack['verbs']

try:
    with open('$SETTINGS') as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

settings['spinnerVerbs'] = {'mode': 'replace', 'verbs': verbs}

# Clean up old statusline if present
if settings.get('statusLine', {}).get('command', '').endswith('vibescc-statusline.sh'):
    del settings['statusLine']

with open('$SETTINGS', 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')
"

    # Add alias
    local alias_line="alias $slug='python3 $LAUNCHER --config $pack_dir'"
    local marker="# vibescc:$slug"

    if grep -q "$marker" "$SHELL_RC" 2>/dev/null; then
        sed -i '' "/$marker/d" "$SHELL_RC"
    fi

    echo "$alias_line $marker" >> "$SHELL_RC"

    info "Installed ${BOLD}$pack_name${RESET} → type ${BOLD}$slug${RESET} to launch"
}

# ── Interactive menu ────────────────────────────────────────────────────
python3 "$SCRIPT_DIR/scripts/banner.py" vibescc
echo -e "  ${DIM}branded Claude Code${RESET}"
echo ""
echo -e "  Pick what to install:"
echo ""

for i in "${!SLUGS[@]}"; do
    num=$((i + 1))
    echo -e "    ${BOLD}$num)${RESET}  ${SLUGS[$i]}  ${DIM}(${NAMES[$i]}, ${BODIES[$i]})${RESET}"
done
echo ""
echo -e "    ${BOLD}a)${RESET}  all of the above"
echo ""

read -p "  Choice [a]: " CHOICE
CHOICE="${CHOICE:-a}"

SELECTED=()

if [ "$CHOICE" = "a" ] || [ "$CHOICE" = "A" ]; then
    SELECTED=("${SLUGS[@]}")
else
    # Parse comma-separated or single numbers
    IFS=', ' read -ra NUMS <<< "$CHOICE"
    for num in "${NUMS[@]}"; do
        idx=$((num - 1))
        if [ "$idx" -ge 0 ] && [ "$idx" -lt "${#SLUGS[@]}" ]; then
            SELECTED+=("${SLUGS[$idx]}")
        else
            error "Invalid choice: $num"
        fi
    done
fi

[ ${#SELECTED[@]} -gt 0 ] || error "Nothing selected"

echo ""

# Install each selected pack
for slug in "${SELECTED[@]}"; do
    python3 "$SCRIPT_DIR/scripts/banner.py" "$slug" 2>/dev/null || true
    install_pack "$slug"
done

# Show summary
echo ""
echo -e "${GREEN}${BOLD}Done!${RESET} Open a new terminal tab, then:"
echo ""
for slug in "${SELECTED[@]}"; do
    echo -e "  ${BOLD}$slug${RESET}              launch with branded crab"
    echo -e "  ${BOLD}$slug --resume${RESET}     resume last conversation"
done
echo ""
echo -e "Verbs are active from the last installed pack."
echo -e "To uninstall: ${BOLD}./uninstall.sh${RESET}"
