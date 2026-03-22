#!/usr/bin/env python3
"""
img-to-pack.py — Convert a small PNG/JPG image into a VibesCC mascot pack.

Uses half-block Unicode characters (▀▄█) to render pixel art in the terminal.
Each character cell represents 2 vertical pixels using foreground/background colors.

Usage:
    python3 img-to-pack.py input.png --name "Company Name" --slug company --width 30
    python3 img-to-pack.py logo.jpg --name "YC" --slug yc --width 24 --output ./packs/yc/

Requirements:
    pip install Pillow
"""

import argparse
import json
import os
import sys

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow")
    sys.exit(1)


def rgb_to_ansi(r, g, b):
    """Convert RGB to ANSI 24-bit color escape code."""
    return f"\\033[38;2;{r};{g};{b}m"


def rgb_to_ansi_bg(r, g, b):
    """Convert RGB to ANSI 24-bit background color escape code."""
    return f"\\033[48;2;{r};{g};{b}m"


def is_transparent(pixel, threshold=128):
    """Check if a pixel is transparent (for RGBA images)."""
    if len(pixel) == 4:
        return pixel[3] < threshold
    return False


def image_to_halfblock(img, target_width=30):
    """
    Convert an image to half-block Unicode art.

    Each character cell is 1 col × 2 rows of pixels.
    Top pixel = foreground color with ▀
    Bottom pixel = background color
    If both same = █ with that color
    If top transparent = ▄ with bottom as foreground
    If bottom transparent = ▀ with top as foreground
    If both transparent = space
    """
    # Resize: width = target_width, height = proportional but must be even
    aspect = img.height / img.width
    target_height = int(target_width * aspect * 2)  # *2 because chars are ~2:1
    if target_height % 2 != 0:
        target_height += 1

    img = img.resize((target_width, target_height), Image.LANCZOS)

    if img.mode != "RGBA":
        img = img.convert("RGBA")

    pixels = list(img.getdata())
    width = img.width

    lines = []
    reset = "\\033[0m"

    for row in range(0, target_height, 2):
        line = ""
        for col in range(target_width):
            top_idx = row * width + col
            bot_idx = (row + 1) * width + col if (row + 1) < target_height else None

            top = pixels[top_idx]
            bot = pixels[bot_idx] if bot_idx is not None else (0, 0, 0, 0)

            top_trans = is_transparent(top)
            bot_trans = is_transparent(bot)

            if top_trans and bot_trans:
                line += " "
            elif top_trans:
                # Only bottom pixel visible
                fg = rgb_to_ansi(bot[0], bot[1], bot[2])
                line += f"{fg}▄{reset}"
            elif bot_trans:
                # Only top pixel visible
                fg = rgb_to_ansi(top[0], top[1], top[2])
                line += f"{fg}▀{reset}"
            else:
                # Both visible: top = fg ▀, bottom = bg
                fg = rgb_to_ansi(top[0], top[1], top[2])
                bg = rgb_to_ansi_bg(bot[0], bot[1], bot[2])
                line += f"{fg}{bg}▀{reset}"

        lines.append(line)

    return lines


def generate_statusline_script(slug, primary_color, lines):
    """Generate the statusline.sh script for a brand pack."""
    # Parse hex color
    pc = primary_color.lstrip("#")
    r, g, b = int(pc[0:2], 16), int(pc[2:4], 16), int(pc[4:6], 16)

    script = f"""#!/bin/bash
set -euo pipefail

# VibesCC Statusline — {slug} Brand Pack
INPUT=$(cat)

extract_json() {{
  local key="$1"
  echo "$INPUT" | grep -o "\\"$key\\"[[:space:]]*:[[:space:]]*[^,}}]*" | head -1 | sed 's/.*:[[:space:]]*//' | tr -d '"'
}}

extract_nested() {{
  local key="$1"
  echo "$INPUT" | grep -o "\\"$key\\"[[:space:]]*:[[:space:]]*[0-9.]*" | head -1 | sed 's/.*:[[:space:]]*//' | tr -d '"'
}}

CURRENT_DIR=$(extract_json "current_dir")
CONTEXT_PCT=$(extract_nested "used_percentage")

BRANCH=""
if git -C "$CURRENT_DIR" rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  BRANCH=$(git -C "$CURRENT_DIR" branch --show-current 2>/dev/null || echo "")
fi

BRAND="\\033[38;2;{r};{g};{b}m"
GRAY="\\033[90m"
RESET="\\033[0m"
BOLD="\\033[1m"

if [ -n "$CONTEXT_PCT" ]; then
  CTX_INT=${{CONTEXT_PCT%.*}}
  if [ "$CTX_INT" -lt 40 ]; then
    CTX_COLOR="\\033[32m"
  elif [ "$CTX_INT" -lt 70 ]; then
    CTX_COLOR="\\033[33m"
  else
    CTX_COLOR="\\033[31m"
  fi
  CTX_DISPLAY="${{CTX_COLOR}}${{CTX_INT}}%${{RESET}}"
else
  CTX_DISPLAY="${{GRAY}}--${{RESET}}"
fi

OUTPUT="${{BRAND}}${{BOLD}}{slug.upper()}${{RESET}}"

if [ -n "$BRANCH" ]; then
  OUTPUT="${{OUTPUT}} ${{GRAY}}|${{RESET}} ${{BRANCH}}"
fi

OUTPUT="${{OUTPUT}} ${{GRAY}}|${{RESET}} ctx ${{CTX_DISPLAY}}"

echo -e "$OUTPUT"
"""
    return script


def create_pack(input_image, name, slug, target_width, output_dir, primary_color, verbs):
    """Create a complete brand pack from an image."""
    os.makedirs(output_dir, exist_ok=True)

    # Convert image
    img = Image.open(input_image)
    art_lines = image_to_halfblock(img, target_width)

    # Write mascot.txt
    mascot_content = "\n".join(art_lines)
    with open(os.path.join(output_dir, "mascot.txt"), "w") as f:
        f.write(mascot_content)

    # Write pack.json
    pack_config = {
        "name": name,
        "slug": slug,
        "description": f"{name}-branded Claude Code experience",
        "colors": {
            "primary": primary_color,
            "secondary": "#FFFFFF",
            "accent": "#1A1A1A",
        },
        "verbs": verbs,
        "mascot": {
            "name": f"{name} Crab",
            "description": f"Claude's crab with {name} branding",
            "art_file": "mascot.txt",
            "width": target_width,
            "height": len(art_lines),
        },
    }
    with open(os.path.join(output_dir, "pack.json"), "w") as f:
        json.dump(pack_config, f, indent=2)

    # Write statusline.sh
    statusline = generate_statusline_script(slug, primary_color, art_lines)
    statusline_path = os.path.join(output_dir, "statusline.sh")
    with open(statusline_path, "w") as f:
        f.write(statusline)
    os.chmod(statusline_path, 0o755)

    print(f"Pack created at {output_dir}/")
    print(f"  mascot.txt  — {target_width}x{len(art_lines)} half-block art")
    print(f"  pack.json   — {len(verbs)} verbs")
    print(f"  statusline.sh")


def main():
    parser = argparse.ArgumentParser(description="Convert an image to a VibesCC brand pack")
    parser.add_argument("image", help="Input image (PNG/JPG)")
    parser.add_argument("--name", required=True, help="Company name")
    parser.add_argument("--slug", required=True, help="Short slug (e.g. 'yc')")
    parser.add_argument("--width", type=int, default=30, help="Art width in columns (default: 30)")
    parser.add_argument("--output", default=None, help="Output directory (default: ./packs/<slug>/)")
    parser.add_argument("--color", default="#FF6600", help="Primary brand color hex (default: #FF6600)")
    parser.add_argument(
        "--verbs",
        nargs="+",
        default=["Vibing", "Building", "Shipping", "Hacking"],
        help="Custom spinner verbs",
    )

    args = parser.parse_args()
    output_dir = args.output or f"./packs/{args.slug}/"

    create_pack(args.image, args.name, args.slug, args.width, output_dir, args.color, args.verbs)


if __name__ == "__main__":
    main()
