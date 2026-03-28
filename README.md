# Vibes

Branded Claude Code. Custom crab colors + spinner verbs. One command.

```
yc        →  orange crab     stripe    →  purple crab
vercel    →  black crab      supabase  →  green crab
```

## Install

```bash
bunx vibes
```

Or with git:

```bash
git clone https://github.com/djessicatony/vibescc.git
cd vibescc
./install.sh
```

Pick packs, open a new tab, done:

```bash
yc                                    # orange crab
stripe --resume                       # purple crab, resume session
yc --verbs looksmaxxing               # orange crab, custom verbs
yc --dangerously-skip-permissions     # all claude flags work
```

Uninstall: `bunx vibes uninstall` or `./uninstall.sh`

## How it works

A PTY wrapper intercepts Claude's ANSI output and swaps the crab's color bytes before they hit your terminal. No binary patching. Pixel-perfect to the original — same crab, different paint. Survives Claude Code updates.

**Crab colors** = per tab. Different crabs in different tabs.

**Spinner verbs** = global (`~/.claude/settings.json`). Last write wins. Use `--verbs <pack>` to switch.

## Brand packs

| Pack | Body | Eyes |
|------|------|------|
| **yc** | `#FB651E` | `#FFFFFF` |
| **stripe** | `#635BFF` | `#FFFFFF` |
| **vercel** | `#000000` | `#FFFFFF` |
| **supabase** | `#3ECF8E` | `#FAFAFA` |
| **looksmaxxing** | `#1A1A2E` | `#E94560` |

### Create your own

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

Re-run installer to get the alias.

## Requirements

- Python 3.6+ (stdlib only)
- Claude Code in PATH
- macOS or Linux

## License

MIT
