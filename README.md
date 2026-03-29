# VibesCC

Branded Claude Code. Custom crab + spinner verbs. One command.

```
yc        →  orange crab     stripe    →  purple crab
vercel    →  black crab      supabase  →  green crab
```

## Install

```bash
bunx vibescc
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
yc --verbs looksmaxxing               # swap verbs
yc --dangerously-skip-permissions     # all claude flags work
```

Uninstall: `bunx vibescc uninstall` or `./uninstall.sh`

## How it works

A PTY wrapper intercepts Claude's ANSI output and swaps the crab's color bytes before they hit your terminal. No binary patching. Pixel-perfect to the original — same crab, different paint. Survives Claude Code updates.

**Crab** = per tab. Different crabs in different tabs.

**Verbs** = global (`~/.claude/settings.json`). Use `--verbs <pack>` to switch.

## Brand packs

| Pack | Crab |
|------|------|
| **yc** | orange, white eyes |
| **stripe** | purple, white eyes |
| **vercel** | black, white eyes |
| **supabase** | green, white eyes |
| **looksmaxxing** | dark, red eyes |

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
