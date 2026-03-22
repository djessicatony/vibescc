# VibesCC — Working Versions

## Current working version

**Commit:** `1956f6d`
**Date:** 2026-03-23
**Description:** Fix mascot renderer: run-length optimization, ANSI prefix to prevent statusline trimming

Rollback command:
```bash
git checkout 1956f6d -- .
```

### What works in this version
- img-to-pack.py converts 16x16 PNG sprites to half-block Unicode art
- Run-length grouped escape codes (keeps byte count low for statusline)
- ANSI reset prefix on every line prevents Claude Code's whitespace stripping
- Non-breaking spaces for transparent pixels
- Nearest-neighbor scaling (no pixel art blurring)
- YC test pack with user's custom sprite
- Spinner verbs via settings.json
- Statusline rendering with git branch + context %

---

## Initial scaffold

**Commit:** `72f79c4`
**Date:** 2026-03-23
**Description:** Initial vibescc plugin scaffold

Rollback command:
```bash
git checkout 72f79c4 -- .
```
