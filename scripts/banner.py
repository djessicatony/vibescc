#!/usr/bin/env python3
"""
banner.py — Render brand names as gradient block-letter art.

Usage:
    python3 banner.py vibescc                    # default gradient
    python3 banner.py YC --from FB651E --to FFAA44
    python3 banner.py STRIPE --from 635BFF --to 8B7FFF
"""

import sys

# ── Block letter font (6 rows tall) ────────────────────────────────────
FONT = {
    "A": [
        " █████╗ ",
        "██╔══██╗",
        "███████║",
        "██╔══██║",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ],
    "B": [
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔══██╗",
        "██████╔╝",
        "╚═════╝ ",
    ],
    "C": [
        " ██████╗",
        "██╔════╝",
        "██║     ",
        "██║     ",
        "╚██████╗",
        " ╚═════╝",
    ],
    "D": [
        "██████╗ ",
        "██╔══██╗",
        "██║  ██║",
        "██║  ██║",
        "██████╔╝",
        "╚═════╝ ",
    ],
    "E": [
        "███████╗",
        "██╔════╝",
        "█████╗  ",
        "██╔══╝  ",
        "███████╗",
        "╚══════╝",
    ],
    "F": [
        "███████╗",
        "██╔════╝",
        "█████╗  ",
        "██╔══╝  ",
        "██║     ",
        "╚═╝     ",
    ],
    "G": [
        " ██████╗ ",
        "██╔════╝ ",
        "██║  ███╗",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ],
    "H": [
        "██╗  ██╗",
        "██║  ██║",
        "███████║",
        "██╔══██║",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ],
    "I": [
        "██╗",
        "██║",
        "██║",
        "██║",
        "██║",
        "╚═╝",
    ],
    "K": [
        "██╗  ██╗",
        "██║ ██╔╝",
        "█████╔╝ ",
        "██╔═██╗ ",
        "██║  ██╗",
        "╚═╝  ╚═╝",
    ],
    "L": [
        "██╗     ",
        "██║     ",
        "██║     ",
        "██║     ",
        "███████╗",
        "╚══════╝",
    ],
    "M": [
        "███╗   ███╗",
        "████╗ ████║",
        "██╔████╔██║",
        "██║╚██╔╝██║",
        "██║ ╚═╝ ██║",
        "╚═╝     ╚═╝",
    ],
    "N": [
        "███╗   ██╗",
        "████╗  ██║",
        "██╔██╗ ██║",
        "██║╚██╗██║",
        "██║ ╚████║",
        "╚═╝  ╚═══╝",
    ],
    "O": [
        " ██████╗ ",
        "██╔═══██╗",
        "██║   ██║",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ],
    "P": [
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔═══╝ ",
        "██║     ",
        "╚═╝     ",
    ],
    "R": [
        "██████╗ ",
        "██╔══██╗",
        "██████╔╝",
        "██╔══██╗",
        "██║  ██║",
        "╚═╝  ╚═╝",
    ],
    "S": [
        "███████╗",
        "██╔════╝",
        "███████╗",
        "╚════██║",
        "███████║",
        "╚══════╝",
    ],
    "T": [
        "████████╗",
        "╚══██╔══╝",
        "   ██║   ",
        "   ██║   ",
        "   ██║   ",
        "   ╚═╝   ",
    ],
    "U": [
        "██╗   ██╗",
        "██║   ██║",
        "██║   ██║",
        "██║   ██║",
        "╚██████╔╝",
        " ╚═════╝ ",
    ],
    "V": [
        "██╗   ██╗",
        "██║   ██║",
        "██║   ██║",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
        "  ╚═══╝  ",
    ],
    "W": [
        "██╗    ██╗",
        "██║    ██║",
        "██║ █╗ ██║",
        "██║███╗██║",
        "╚███╔███╔╝",
        " ╚══╝╚══╝ ",
    ],
    "X": [
        "██╗  ██╗",
        "╚██╗██╔╝",
        " ╚███╔╝ ",
        " ██╔██╗ ",
        "██╔╝ ██╗",
        "╚═╝  ╚═╝",
    ],
    "Y": [
        "██╗   ██╗",
        "╚██╗ ██╔╝",
        " ╚████╔╝ ",
        "  ╚██╔╝  ",
        "   ██║   ",
        "   ╚═╝   ",
    ],
    "Z": [
        "███████╗",
        "╚══███╔╝",
        "  ███╔╝ ",
        " ███╔╝  ",
        "███████╗",
        "╚══════╝",
    ],
    " ": [
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
        "   ",
    ],
}


def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def colorize_char(char, r, g, b):
    if char in (" ", ""):
        return char
    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"


def render_banner(text, color_from, color_to, indent=4):
    text = text.upper()
    rows = [[] for _ in range(6)]

    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for i, line in enumerate(glyph):
            rows[i].append(line)

    # Join rows and apply horizontal gradient
    output = []
    for row_parts in rows:
        full_line = "".join(row_parts)
        total = max(len(full_line), 1)
        colored = ""
        pos = 0
        for char in full_line:
            t = pos / total
            r, g, b = lerp_color(color_from, color_to, t)
            colored += colorize_char(char, r, g, b)
            pos += 1
        output.append(" " * indent + colored)

    return "\n".join(output)


# ── Preset gradients per brand ──────────────────────────────────────────
PRESETS = {
    "vibescc":  {"text": "VIBESCC",  "from": "FF6B6B", "to": "C084FC"},
    "yc":       {"text": "YC",       "from": "FB651E", "to": "FFAA44"},
    "stripe":   {"text": "STRIPE",   "from": "635BFF", "to": "A89BFF"},
    "vercel":   {"text": "VERCEL",   "from": "888888", "to": "FFFFFF"},
    "supabase": {"text": "SUPABASE", "from": "249361", "to": "3ECF8E"},
}


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="Text to render (or preset name)")
    parser.add_argument("--from", dest="color_from", default=None)
    parser.add_argument("--to", dest="color_to", default=None)
    parser.add_argument("--indent", type=int, default=4)
    args = parser.parse_args()

    name = args.name.lower()

    if name in PRESETS and not args.color_from:
        preset = PRESETS[name]
        text = preset["text"]
        c_from = hex_to_rgb(preset["from"])
        c_to = hex_to_rgb(preset["to"])
    else:
        text = args.name.upper()
        c_from = hex_to_rgb(args.color_from or "FFFFFF")
        c_to = hex_to_rgb(args.color_to or args.color_from or "FFFFFF")

    print()
    print(render_banner(text, c_from, c_to, args.indent))
    print()


if __name__ == "__main__":
    main()
