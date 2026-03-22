---
name: vibescc:list
description: List all available VibesCC brand packs
allowed-tools: Bash(*), Read
---

# List Available Brand Packs

List all available VibesCC brand packs by scanning `${CLAUDE_PLUGIN_ROOT}/packs/`.

For each pack directory found:
1. Read `pack.json`
2. Display the pack name, description, number of verbs, and brand colors
3. Show a preview of 3-4 sample verbs

Format the output as a clean list the user can browse.
