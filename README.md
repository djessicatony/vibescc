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

Press `y`, open a new tab, done.

Uninstall: `bunx vibescc uninstall` or `./uninstall.sh`

## Usage

```bash
yc                          # orange crab + whatever verbs are set
stripe                      # purple crab + whatever verbs are set
stripe --resume             # all claude flags work
stripe --dangerously-skip-permissions
```

### Mix and match

Crab colors and verbs are independent. The crab comes from the alias, verbs come from `~/.claude/settings.json`.

**Custom crab, default verbs** — just run the alias without `--verbs`:

```bash
yc                          # orange crab, Claude's default verbs
```

**Custom crab, custom verbs** — pass `--verbs` once, it sticks:

```bash
yc --verbs looksmaxxing     # orange crab + looksmaxxing verbs from now on
yc                          # still looksmaxxing verbs (they persist)
stripe                      # purple crab + still looksmaxxing verbs
```

**Default crab, custom verbs** — just run `claude` after setting verbs:

```bash
yc --verbs looksmaxxing     # set verbs
claude                      # default crab + looksmaxxing verbs
```

**Switch verbs anytime:**

```bash
yc --verbs stripe           # switch to Stripe verbs
yc --verbs yc               # switch to YC verbs
yc --verbs looksmaxxing     # switch to looksmaxxing verbs
```

**Add verbs to Claude's defaults** instead of replacing — edit `~/.claude/settings.json`:

```json
{
  "spinnerVerbs": {
    "mode": "append",
    "verbs": ["Mogging", "Looksmaxxing", "Mewing"]
  }
}
```

With `"append"`, your verbs get mixed into Claude's ~100 default verbs. With `"replace"`, only your verbs show.

## How it works

A PTY wrapper intercepts Claude's ANSI output and swaps the crab's color bytes before they hit your terminal. No binary patching. Pixel-perfect to the original — same crab, different paint. Survives Claude Code updates.

**Crab** = per tab. Different crabs in different tabs.

**Verbs** = global (`~/.claude/settings.json`). Use `--verbs <pack>` to switch. Last write wins across all tabs.

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

Re-run `bunx vibescc` or `./install.sh` to get the alias.

## Requirements

- Python 3.6+ (stdlib only)
- Claude Code in PATH
- macOS or Linux

## License

MIT
