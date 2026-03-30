# VibesCC — Branded Claude Code

VibesCC recolors Claude Code's crab mascot and spinner verbs to match your company or vibe. A PTY wrapper intercepts the ANSI output and swaps color bytes before they hit your terminal — pixel-perfect to the original, just different paint. No binary patching. Survives Claude Code updates.

```
yc           →  orange crab        stripe      →  purple crab
vercel       →  black crab         supabase    →  green crab
looksmaxxing →  gray crab, red eyes
```

## Installation

**Requirements:** Python 3.6+, Claude Code in PATH, macOS or Linux

### One-Line Install

```bash
bunx vibescc
```

### Manual Install

```bash
git clone https://github.com/djessicatony/vibescc.git
cd vibescc
./install.sh
```

Press `y` to proceed. Open a new terminal tab, done.

To uninstall: `bunx vibescc uninstall` or `./uninstall.sh`

## Usage

Each brand pack registers a shell alias that launches Claude Code with a recolored crab:

```bash
yc                                    # orange crab
stripe                                # purple crab
supabase                              # green crab
vercel                                # black crab
looksmaxxing                          # gray crab, red eyes
```

All Claude Code flags work as normal:

```bash
yc --resume
stripe --dangerously-skip-permissions
yc --verbs looksmaxxing               # swap spinner verbs
```

### Mixing Crab Colors and Verbs

Crab colors and spinner verbs are independent. The crab comes from the alias you launch with. Verbs persist in `~/.claude/settings.json` until you explicitly change them.

| What you want | How to do it |
|---------------|-------------|
| Custom crab, default verbs | `yc` (just the alias, no `--verbs`) |
| Custom crab, custom verbs | `yc --verbs looksmaxxing` (set once, sticks) |
| Default crab, custom verbs | Set verbs with `--verbs`, then run `claude` directly |
| Add verbs to Claude's defaults | Set `"mode": "append"` in `~/.claude/settings.json` |

## How It Works

Claude Code renders its crab mascot ("Clawd") using Unicode quadrant block characters with ANSI color codes. VibesCC spawns `claude` inside a pseudoterminal and does byte-level find-and-replace on the output stream:

```
You see branded crab ← replace colors ← PTY master ← PTY slave ← claude
```

| What gets replaced | Original | Your brand color |
|---|---|---|
| Crab body, border, spinner | `rgb(215,119,87)` | Pack body color |
| Crab eyes | `rgb(0,0,0)` | Pack eye color |
| Shimmer animation | `rgb(245,149,117)` | Body + 30 brightness |
| Alt theme border | `rgb(255,153,51)` | Pack body color |

The crab itself is 8 characters wide, 3 rows tall, with 4 animation poses:

```
 ▐▛███▜▌     ← head + arms
▝▜█████▛▘    ← body
  ▘▘ ▝▝      ← legs
```

Claude has no idea it's being intercepted. The border, thinking spinner, and all branded UI elements get recolored too because they share the same color tokens.

## Brand Packs

Each pack is a directory under `packs/` with a `pack.json`:

```json
{
  "name": "Y Combinator",
  "slug": "yc",
  "colors": { "body": "#FB651E", "eyes": "#FFFFFF" },
  "verbs": ["Demo day prepping", "Fundraising", "Shipping fast"]
}
```

### Included Packs

| Pack | Body | Eyes | Crab |
|------|------|------|------|
| **yc** | `#FB651E` | `#FFFFFF` | Orange body, white eyes |
| **stripe** | `#635BFF` | `#FFFFFF` | Purple body, white eyes |
| **vercel** | `#000000` | `#FFFFFF` | Black body, white eyes |
| **supabase** | `#3ECF8E` | `#FAFAFA` | Green body, white eyes |
| **looksmaxxing** | `#4E4E4E` | `#FF0004` | Gray body, red eyes |

### Create Your Own

```bash
mkdir packs/mycompany
cat > packs/mycompany/pack.json << 'EOF'
{
  "name": "My Company",
  "slug": "mycompany",
  "colors": { "body": "#FF0000", "eyes": "#FFFFFF" },
  "verbs": ["Shipping", "Building", "Deploying"]
}
EOF
```

Re-run `bunx vibescc` or `./install.sh` to register the alias.

## Project Structure

```
vibescc/
  scripts/
    vibescc-launch.py       # PTY wrapper — the entire product
    banner.py               # Gradient block-letter renderer for installer
    yc-claude               # Convenience launcher for YC
  packs/
    yc/pack.json            # Colors + verbs per brand
    stripe/pack.json
    vercel/pack.json
    supabase/pack.json
    looksmaxxing/pack.json
  bin/
    vibes.mjs               # npx/bunx installer entry point
  commands/                  # Claude Code plugin commands (optional)
    install.md               # /vibescc:install
    uninstall.md             # /vibescc:uninstall
    list.md                  # /vibescc:list
  install.sh                 # Git clone installer
  uninstall.sh               # Removes aliases and verbs
```

## Limitations

- **Crab colors are per-tab, verbs are global** — you can have different crabs in different tabs, but verbs are shared across all sessions via `~/.claude/settings.json`
- **Colors only** — can't change the crab's shape or add logos to it
- **RGB themes only** — if Claude Code falls back to ANSI-16 colors (rare on modern terminals), the color codes differ and won't be matched
- **Verb color = crab color** — the spinner text, border, and crab all share the same color token, so they all change together

## License

MIT
