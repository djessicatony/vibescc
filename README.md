# VibesCC

Company-branded Claude Code in one command. Recolors the crab, swaps the spinner verbs.

```
yc        →  orange crab
stripe    →  purple crab
vercel    →  black crab
supabase  →  green crab
```

No binary patching. No hacks. A PTY wrapper intercepts the ANSI output and repaints the crab before it hits your terminal. Pixel-perfect to Claude Code's original — same characters, same animation, same poses. Just different paint.

## Install

```bash
git clone https://github.com/djessicatony/vibescc.git
cd vibescc
./install.sh
```

The installer shows all available packs. Pick one, pick several, or hit enter for all. It adds shell aliases and sets your spinner verbs.

Then open a new terminal tab:

```bash
yc                    # launch claude with orange crab
stripe                # launch claude with purple crab
```

All claude flags work:

```bash
yc --resume
yc --dangerously-skip-permissions
stripe --resume
```

To uninstall everything: `./uninstall.sh`

## What you need to know

**Crab colors** = per tab. Each alias launches its own PTY wrapper with its own color replacement. You can have a purple crab in one tab and an orange crab in another.

**Spinner verbs** = global. They live in `~/.claude/settings.json` which is shared across all Claude sessions. The last write wins. There's no way around this — it's how Claude Code works.

To switch verbs:

```bash
yc --verbs looksmaxxing     # sets looksmaxxing verbs globally, launches YC crab
stripe --verbs stripe        # sets stripe verbs globally, launches Stripe crab
```

Without `--verbs`, whatever verbs are in settings.json stay. The installer sets verbs from the last pack you installed.

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

| Pack | Body | Eyes |
|------|------|------|
| **yc** | `#FB651E` orange | `#FFFFFF` white |
| **stripe** | `#635BFF` purple | `#FFFFFF` white |
| **vercel** | `#000000` black | `#FFFFFF` white |
| **supabase** | `#3ECF8E` green | `#FAFAFA` white |
| **looksmaxxing** | default crab | default eyes |

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
```

Then re-run `./install.sh` to get the alias.

## How it works

Claude Code renders its crab ("Clawd") using Unicode quadrant blocks with two ANSI colors:

```
 ▐▛███▜▌     ← head
▝▜█████▛▘    ← body
  ▘▘ ▝▝      ← legs
```

The PTY wrapper spawns `claude` inside a pseudoterminal and does byte-level find-and-replace on the ANSI stream before it reaches your terminal:

```
You see colored crab ← replace colors ← PTY master ← PTY slave ← claude
```

| What gets replaced | Original | Your brand |
|---|---|---|
| `clawd_body` | `rgb(215,119,87)` | pack body color |
| `clawd_background` | `rgb(0,0,0)` | pack eye color |
| `claudeShimmer` | `rgb(245,149,117)` | body + 30 brightness |

Claude has no idea it's being intercepted. The border, thinking spinner, and all branded UI elements get recolored too because they share the same color tokens.

## Requirements

- Python 3.6+ (stdlib only — no pip install needed)
- Claude Code installed and in PATH
- macOS or Linux

## Limitations

- **Crab colors are per-tab, verbs are global** — can't have different verbs in different tabs
- **Colors only** — can't change the crab's shape or add logos
- **RGB themes only** — ANSI-16 fallback themes use different color codes and won't be matched (rare)

## License

MIT
