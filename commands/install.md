---
name: vibescc:install
description: Install a company brand pack (mascot + spinner verbs) for Claude Code
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
- `mascot`: The statusline mascot art file reference
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

## Step 4: Install the statusline

Copy the statusline script from the pack and configure it:

1. Read `${CLAUDE_PLUGIN_ROOT}/packs/<pack-name>/statusline.sh`
2. Write it to `~/.claude/vibescc-statusline.sh`
3. Make it executable: `chmod +x ~/.claude/vibescc-statusline.sh`
4. Update `~/.claude/settings.json` to add:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/vibescc-statusline.sh"
  }
}
```

## Step 5: Confirm

Tell the user:
- Brand pack installed successfully
- They need to restart Claude Code for changes to take effect
- They can uninstall with `/vibescc:uninstall`
