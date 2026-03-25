# VibesCC

Company-branded Claude Code in one command. Recolors the crab, swaps the spinner verbs.

```
yc        →  orange crab, YC startup verbs
stripe    →  purple crab, payments verbs
vercel    →  black crab, deployment verbs
supabase  →  green crab, database verbs
```

No binary patching. No hacks. A PTY wrapper intercepts the ANSI output and swaps color bytes before they hit your terminal. The crab is pixel-perfect to Claude Code's original — same characters, same animation, same poses. Just different paint.

## How it works

Claude Code renders its crab mascot ("Clawd") using Unicode quadrant block characters with two theme colors:

| Token | Default | ANSI code |
|-------|---------|-----------|
| `clawd_body` | `rgb(215,119,87)` | `\x1b[38;2;215;119;87m` |
| `clawd_background` | `rgb(0,0,0)` | `\x1b[48;2;0;0;0m` |

VibesCC spawns `claude` inside a pseudoterminal and does a byte-level find-and-replace on the ANSI stream:

```
Terminal ← filtered ANSI ← PTY master ← PTY slave ← claude
                ↑
     38;2;215;119;87 → 38;2;251;101;30  (body)
     48;2;0;0;0      → 48;2;255;255;255 (eyes)
```

Claude has no idea it's being intercepted. All features, flags, and keybindings work identically.

## Quick start

```bash
git clone https://github.com/djessicatony/vibescc.git
cd vibescc

# Launch with a brand pack
python3 scripts/vibescc-launch.py --config packs/yc

# Or with raw colors
python3 scripts/vibescc-launch.py --body "#FB651E" --eyes "#FFFFFF"

# Pass flags through to claude
python3 scripts/vibescc-launch.py --config packs/stripe -- --resume
```

### Shell aliases (recommended)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias yc='python3 ~/path/to/vibescc/scripts/vibescc-launch.py --config ~/path/to/vibescc/packs/yc'
alias stripe='python3 ~/path/to/vibescc/scripts/vibescc-launch.py --config ~/path/to/vibescc/packs/stripe'
alias vercel='python3 ~/path/to/vibescc/scripts/vibescc-launch.py --config ~/path/to/vibescc/packs/vercel'
alias supabase='python3 ~/path/to/vibescc/scripts/vibescc-launch.py --config ~/path/to/vibescc/packs/supabase'
```

Then just type `yc` instead of `claude`.

## Brand packs

Each pack is a directory under `packs/` with a `pack.json`:

```json
{
  "name": "Y Combinator",
  "slug": "yc",
  "colors": {
    "body": "#FB651E",
    "eyes": "#FFFFFF"
  },
  "verbs": [
    "Demo day prepping",
    "Fundraising",
    "Growth hacking"
  ]
}
```

### Included packs

| Pack | Body | Eyes | Crab |
|------|------|------|------|
| **yc** | `#FB651E` | `#FFFFFF` | Orange body, white eyes |
| **stripe** | `#635BFF` | `#FFFFFF` | Purple body, white eyes |
| **vercel** | `#000000` | `#FFFFFF` | Black body, white eyes |
| **supabase** | `#3ECF8E` | `#FAFAFA` | Green body, white eyes |

### Create your own

```bash
mkdir packs/mycompany
cat > packs/mycompany/pack.json << 'EOF'
{
  "name": "My Company",
  "slug": "mycompany",
  "colors": {
    "body": "#FF0000",
    "eyes": "#FFFFFF"
  },
  "verbs": [
    "Doing the thing",
    "Shipping features",
    "Fixing bugs"
  ]
}
EOF

python3 scripts/vibescc-launch.py --config packs/mycompany
```

## Spinner verbs

Brand packs also include custom spinner verbs — the text that shows while Claude is thinking ("Thinking...", "Analyzing...", etc.). VibesCC replaces these with company-flavored alternatives.

To install verbs into Claude Code (persists across sessions):

```
# Inside Claude Code, with vibescc as a plugin:
/vibescc:install
```

This writes `spinnerVerbs` to `~/.claude/settings.json`. The PTY wrapper handles crab colors separately — verbs and colors are independent.

## Architecture

```
vibescc/
├── scripts/
│   ├── vibescc-launch.py    # PTY wrapper — the entire product
│   └── yc-claude            # Convenience launcher for YC
├── packs/
│   ├── yc/pack.json         # Colors + verbs per brand
│   ├── stripe/pack.json
│   ├── vercel/pack.json
│   └── supabase/pack.json
├── commands/                 # Claude Code plugin commands
│   ├── install.md            # /vibescc:install (applies verbs)
│   ├── uninstall.md          # /vibescc:uninstall (removes verbs)
│   └── list.md               # /vibescc:list (shows packs)
└── .claude-plugin/
    └── plugin.json           # Plugin manifest
```

### Why PTY and not binary patching?

| | PTY wrapper | Binary patching (tweakcc) |
|---|---|---|
| Survives updates | Yes | No — must re-patch |
| Dependencies | Python 3 (stdlib only) | Node.js + tweakcc |
| Risk | Zero — doesn't touch claude | Medium — modifies cli.js |
| What it can change | Colors only | Anything in the JS bundle |
| Setup | One alias | Install tweakcc, configure, apply |

The PTY approach is intentionally limited. It does one thing — swap colors in the ANSI stream. That's why it's ~200 lines of Python with zero dependencies and survives every Claude Code update.

### How the crab is built

Claude Code's crab is 8 characters wide, 3 rows tall, built from Unicode quadrant blocks:

```
 ▐▛███▜▌     ← row 1: arms + head (r1L + r1E + r1R)
▝▜█████▛▘    ← row 2: sides + chest (r2L + █████ + r2R)
  ▘▘ ▝▝      ← row 3: legs
```

It has 4 animation poses (`default`, `look-left`, `look-right`, `arms-up`) that change the quadrant blocks for the eyes and arms. All poses use the same two colors:

- **`clawd_body`** (foreground) — the shell, arms, legs
- **`clawd_background`** (background) — the eyes, chest fill

VibesCC replaces both color codes in the terminal output stream. Every pose, every animation frame gets recolored.

## Requirements

- Python 3.6+ (uses only stdlib: `pty`, `select`, `termios`, `fcntl`)
- Claude Code installed and in PATH
- macOS or Linux (PTY is a Unix concept)

## Limitations

- **Colors only** — can't change the crab's shape, add logos, or modify text
- **RGB themes only** — if Claude Code falls back to ANSI-16 colors (rare), the color codes differ and won't be matched
- **Stream splitting** — in theory, a color code could split across two read() chunks at a buffer boundary; in practice this doesn't happen with 4096-byte reads
- **Eye color is global** — `clawd_background` (`48;2;0;0;0`) is specifically the crab's background color, but if other UI elements happen to use the exact same RGB black, they'd also be recolored

## License

MIT
