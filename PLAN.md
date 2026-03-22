# VibesCC — Branded Claude Code Experiences

Company-branded mascots + spinner verbs for Claude Code, distributed as a plugin.

## What it does

Companies install VibesCC and pick their brand pack. They get:
- **Custom mascot** in the statusline (pixel art rendered with Unicode half-blocks)
- **Custom spinner verbs** ("Demo day prepping", "Office houring", etc.)
- One command to install, one to uninstall

## Architecture

```
vibescc/
├── .claude-plugin/plugin.json     # Plugin manifest
├── commands/
│   ├── install.md                 # /vibescc:install — apply a brand pack
│   ├── uninstall.md               # /vibescc:uninstall — revert to defaults
│   ├── list.md                    # /vibescc:list — show available packs
│   └── preview.md                 # /vibescc:preview — preview before installing
├── packs/
│   ├── yc/                        # Y Combinator pack (sample)
│   │   ├── pack.json              # Config: name, verbs, colors, mascot ref
│   │   ├── mascot.txt             # Unicode half-block art with ANSI colors
│   │   └── statusline.sh          # Branded statusline script
│   ├── stripe/                    # (future)
│   └── vercel/                    # (future)
└── scripts/
    └── img-to-pack.py             # PNG/JPG → brand pack converter
```

## How it works (Layer B — safe, official APIs only)

### Spinner verbs
Writes to `~/.claude/settings.json`:
```json
{
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": ["Demo day prepping", "Office houring", ...]
  }
}
```
This is a built-in Claude Code feature. No patching. Survives updates.

### Statusline mascot
Writes to `~/.claude/settings.json`:
```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/vibescc-statusline.sh"
  }
}
```
The statusline script:
1. Receives session JSON on stdin (workspace dir, context %)
2. Outputs branded text with ANSI colors: company name, git branch, context usage
3. Can include a compact mascot sprite using Unicode half-block chars (▀▄█)

### Mascot art format
- **NOT images** — terminals render Unicode text, not PNGs
- Half-block characters (▀ ▄ █ ▌ ▐) where each char = 2 vertical pixels
- ANSI 24-bit color codes for full RGB palette
- Typical size: 20-40 cols × 8-14 rows
- Created with `img-to-pack.py` (converts PNG → half-block art)

## How to create a new brand pack

### Option 1: From an image
```bash
pip install Pillow
python3 scripts/img-to-pack.py logo.png \
  --name "Company Name" \
  --slug company \
  --width 24 \
  --color "#FF6600" \
  --verbs "Shipping" "Building" "Deploying"
```
This generates `packs/company/` with pack.json, mascot.txt, and statusline.sh.

### Option 2: Manual
1. Create `packs/<slug>/pack.json` with name, verbs, colors
2. Design mascot art using half-block chars in `mascot.txt`
3. Write or copy a `statusline.sh` script

### Useful Unicode block characters
```
▀ (U+2580) upper half     ▄ (U+2584) lower half
█ (U+2588) full block     ▌ (U+258C) left half
▐ (U+2590) right half     ░ (U+2591) light shade
▒ (U+2592) medium shade   ▓ (U+2593) dark shade
▖▗▘▙▚▛▜▝▞▟ (U+2596-259F) quadrant blocks
```

## Distribution

### For end users
```bash
# In Claude Code:
/plugin install <vibescc-repo-url>
/vibescc:list
/vibescc:install
```

### For companies (white-label)
Ship a fork with only their pack pre-loaded. Single command install:
```bash
/plugin install github.com/company/their-vibescc-fork
/vibescc:install
```

## Roadmap

### Phase 1 — MVP (current)
- [x] Plugin scaffold with install/uninstall/list/preview commands
- [x] YC sample pack (verbs + statusline)
- [x] img-to-pack.py converter
- [ ] Test plugin installation end-to-end
- [ ] Create 2-3 more sample packs (Stripe, Vercel, Shopify)
- [ ] Polish statusline output (test across terminal emulators)

### Phase 2 — Pack marketplace
- [ ] Web UI for designing packs (pick colors, upload logo, write verbs)
- [ ] Pack gallery / marketplace
- [ ] Pack validation CLI (`/vibescc:validate`)
- [ ] Community-submitted packs via PR

### Phase 3 — Layer A (full mascot replacement)
- [ ] Binary patching to replace the home-screen crab
- [ ] Use TweakCC's unpack/repack API as dependency
- [ ] Auto-reapply after Claude Code updates (SessionStart hook)
- [ ] Version-tracking: maintain patches per CC release
- [ ] This is fragile — only offer as opt-in "full takeover" mode

### Dependencies on Anthropic
- **spinnerFrames** ([issue #34541](https://github.com/anthropics/claude-code/issues/34541)) — if Anthropic adds this, we can customize the thinking animation too (the spinning dots), not just the verbs
- **Terminal image protocols** ([issue #2266](https://github.com/anthropics/claude-code/issues/2266)) — if Anthropic adds Sixel/Kitty/iTerm2 support, we can render actual PNG mascots instead of Unicode art
- **Official mascot API** — doesn't exist yet, would make Layer A unnecessary

## Technical notes

### Statusline stdin format
Claude Code pipes this JSON to the statusline command:
```json
{
  "session_id": "...",
  "workspace": {
    "project_dir": "/path/to/project",
    "current_dir": "/path/to/current"
  },
  "context_window": {
    "used_percentage": 42.5
  }
}
```

### Terminal compatibility
- Statusline scripts must handle `process.stdout.columns` being undefined (piped context)
- Use `stty size` via parent TTY for real terminal dimensions
- Test on: iTerm2, Terminal.app, Ghostty, Kitty, WezTerm, VS Code terminal

### Key references
- [Claude Code plugin docs](https://docs.claude.com/en/docs/claude-code/plugins)
- [TweakCC](https://github.com/Piebald-AI/tweakcc) — binary patching tool
- [claude-code-custom-art](https://github.com/ywong137/claude-code-custom-art) — manual mascot replacement guide
- [claude-code-mascot-statusline](https://github.com/TeXmeijin/claude-code-mascot-statusline) — statusline mascot reference implementation
