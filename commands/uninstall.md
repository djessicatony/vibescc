---
name: vibescc:uninstall
description: Remove the current VibesCC brand pack and restore defaults
allowed-tools: Bash(*), Write, Read, Edit
---

# VibesCC Uninstaller

## Step 1: Remove spinner verbs

Read `~/.claude/settings.json` and remove the `spinnerVerbs` key entirely. Write back preserving all other settings.

## Step 2: Remove statusline

Read `~/.claude/settings.json` and remove the `statusLine` key. Write back preserving all other settings.

Delete `~/.claude/vibescc-statusline.sh` if it exists.

## Step 3: Confirm

Tell the user the brand pack has been removed and they should restart Claude Code.
