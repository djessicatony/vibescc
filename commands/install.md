---
name: vibescc:install
description: Install a company brand pack (spinner verbs) for Claude Code
allowed-tools: Bash(*), Write, Read, Edit
---

# VibesCC Brand Pack Installer

You are installing a VibesCC brand pack. Follow these steps:

## Step 1: Ask which company pack to install

Use AskUserQuestion to ask the user which brand pack they want. List available packs by reading the `packs/` directory at `${CLAUDE_PLUGIN_ROOT}/packs/`.

## Step 2: Read the pack config

Read `${CLAUDE_PLUGIN_ROOT}/packs/<pack-name>/pack.json` to get:
- `name`: Company name
- `verbs`: Array of custom spinner verbs
- `colors`: Brand color palette

## Step 3: Apply spinner verbs

Read the user's `~/.claude/settings.json`, merge in:

```json
{
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": ["<verbs from pack>"]
  }
}
```

Write back to `~/.claude/settings.json`, preserving all existing settings.

## Step 4: Confirm

Tell the user:
- Brand pack installed successfully
- Spinner verbs are active immediately
- For custom crab colors, launch with: `python3 <plugin-root>/scripts/vibescc-launch.py --config <plugin-root>/packs/<pack-name>`
- They can uninstall with `/vibescc:uninstall`
