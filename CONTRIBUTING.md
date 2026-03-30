# Contributing to VibesCC

Thanks for your interest in contributing.

## Ways to contribute

- Report bugs
- Propose new brand packs
- Improve the PTY wrapper or installer
- Submit code changes through pull requests

## Development setup

```sh
git clone https://github.com/djessicatony/vibescc.git
cd vibescc
```

Test the installer locally:

```sh
node bin/vibes.mjs
```

Test the PTY wrapper:

```sh
python3 scripts/vibescc-launch.py --body "#FF0000" --eyes "#FFFFFF"
```

## Adding a new brand pack

```sh
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

Test it:

```sh
python3 scripts/vibescc-launch.py --config packs/mycompany
```

## Before opening a pull request

- Test your changes with at least one brand pack
- Verify the installer still works: `node bin/vibes.mjs`
- Check that Claude Code launches and the crab is correctly colored

## Coding expectations

- Keep changes focused and small when possible.
- Follow existing project style and patterns.
- Avoid unrelated refactors in the same pull request.
- The PTY wrapper (`vibescc-launch.py`) uses only Python stdlib — no pip dependencies.

## Commit and PR guidance

- Use clear commit messages (for example: `fix: ...`, `feat: ...`, `pack: ...`).
- Explain what changed and why in the PR description.
- Include test evidence (screenshots or terminal output).

Suggested PR template:

```md
## Summary
- What changed

## Why
- Why this change is needed

## Changes
- File or behavior highlights

## Validation
- Terminal tested (iTerm2, Ghostty, etc.)
- Claude Code version tested against
```

## Reporting bugs

Please include:

- Expected behavior
- Actual behavior
- Reproduction steps
- Environment details (OS, terminal, Claude Code version, Python version)
