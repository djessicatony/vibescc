---
name: vibescc:preview
description: Preview a brand pack's mascot and verbs before installing
allowed-tools: Bash(*), Read
---

# Preview Brand Pack

Preview a VibesCC brand pack without installing it.

## Step 1: Identify pack

If the user specified a pack name, use it. Otherwise, ask which pack to preview using AskUserQuestion, listing packs from `${CLAUDE_PLUGIN_ROOT}/packs/`.

## Step 2: Show preview

1. Read `${CLAUDE_PLUGIN_ROOT}/packs/<pack>/pack.json`
2. Read `${CLAUDE_PLUGIN_ROOT}/packs/<pack>/mascot.txt`
3. Display the mascot art by running: `cat ${CLAUDE_PLUGIN_ROOT}/packs/<pack>/mascot.txt`
4. Display the full verbs list
5. Show the brand colors
6. Show the statusline preview by running: `echo '{"workspace":{"current_dir":"'$(pwd)'"},"context_window":{"used_percentage":42}}' | ${CLAUDE_PLUGIN_ROOT}/packs/<pack>/statusline.sh`

## Step 3: Offer install

Ask if the user wants to install this pack. If yes, tell them to run `/vibescc:install`.
