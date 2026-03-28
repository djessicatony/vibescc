#!/usr/bin/env python3
"""
vibescc-launch.py — PTY wrapper that recolors the Claude Code crab.

Spawns `claude` inside a pseudoterminal, intercepts the ANSI output stream,
and replaces the crab's color codes with company branding colors.

The crab itself is pixel-perfect — same characters, same poses, same animation.
Only the paint changes.

Usage:
    python3 vibescc-launch.py                     # default YC orange
    python3 vibescc-launch.py --body 255,102,0    # custom body RGB
    python3 vibescc-launch.py --config packs/yc   # load from pack.json
    python3 vibescc-launch.py -- --resume          # pass flags to claude
"""

import argparse
import json
import os
import pty
import re
import signal
import struct
import sys
import fcntl
import termios

# ── Original Clawd colors (consistent across CC versions) ──────────────
ORIGINAL_BODY = b"38;2;215;119;87"  # clawd_body / claude: rgb(215,119,87)
ORIGINAL_SHIMMER = b"38;2;245;149;117"  # claudeShimmer: rgb(245,149,117)
ORIGINAL_BG = b"48;2;0;0;0"  # clawd_background: rgb(0,0,0)

# Also match as background colors
ORIGINAL_BODY_AS_BG = b"48;2;215;119;87"
ORIGINAL_SHIMMER_AS_BG = b"48;2;245;149;117"


def make_replacement(r, g, b):
    """Build the replacement byte string for a color."""
    return f"{r};{g};{b}".encode()


def make_shimmer(r, g, b):
    """Generate a lighter shimmer variant of a color (same offset as claude→claudeShimmer)."""
    return (min(r + 30, 255), min(g + 30, 255), min(b + 30, 255))


def build_filter(body_rgb, bg_rgb=None):
    """Return a stateful function that replaces clawd colors in an ANSI byte stream.

    Keeps a small overlap buffer between read() calls to catch color codes
    that get split across chunk boundaries.
    """
    shimmer_rgb = make_shimmer(*body_rgb)
    new_body_fg = b"38;2;" + make_replacement(*body_rgb)
    new_body_bg = b"48;2;" + make_replacement(*body_rgb)
    new_shimmer_fg = b"38;2;" + make_replacement(*shimmer_rgb)
    new_shimmer_bg = b"48;2;" + make_replacement(*shimmer_rgb)

    replacements = [
        (ORIGINAL_BODY, new_body_fg),
        (ORIGINAL_BODY_AS_BG, new_body_bg),
        (ORIGINAL_SHIMMER, new_shimmer_fg),
        (ORIGINAL_SHIMMER_AS_BG, new_shimmer_bg),
    ]

    if bg_rgb:
        new_bg = b"48;2;" + make_replacement(*bg_rgb)
        replacements.append((ORIGINAL_BG, new_bg))

    # Regex to strip terminal identification responses:
    # DCS responses: \x1bP...ST (\x1b\\)  — e.g. ghostty ID
    # DA responses:  \x1b[?...c            — device attributes
    strip_terminal_responses = re.compile(
        rb"\x1bP[^\x1b]*\x1b\\|\x1b\[\?[0-9;]*c"
    )

    def apply(data):
        # Strip terminal ID sequences before they hit the screen
        data = strip_terminal_responses.sub(b"", data)
        # Do replacements
        for old, new in replacements:
            data = data.replace(old, new)
        return data

    return apply


def parse_rgb(s):
    """Parse '255,102,0' or '#FF6600' into (r, g, b) tuple."""
    s = s.strip()
    if s.startswith("#"):
        h = s.lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    parts = s.split(",")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def load_pack_colors(pack_dir):
    """Load body and eyes colors from a vibescc pack.json."""
    pack_json = os.path.join(pack_dir, "pack.json")
    with open(pack_json) as f:
        pack = json.load(f)
    body = parse_rgb(pack["colors"]["body"])
    eyes = parse_rgb(pack["colors"]["eyes"])
    return body, eyes


def resolve_pack_dir(name):
    """Resolve a pack name to its directory. Accepts a path or just a slug."""
    if os.path.isdir(name):
        return name
    # Try relative to script's packs/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    packs_dir = os.path.join(script_dir, "..", "packs")
    candidate = os.path.join(packs_dir, name)
    if os.path.isdir(candidate):
        return candidate
    return None


def apply_verbs(pack_dir):
    """Write a pack's verbs to ~/.claude/settings.json."""
    pack_json = os.path.join(pack_dir, "pack.json")
    with open(pack_json) as f:
        pack = json.load(f)
    verbs = pack.get("verbs", [])
    if not verbs:
        return

    settings_path = os.path.expanduser("~/.claude/settings.json")
    try:
        with open(settings_path) as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    settings["spinnerVerbs"] = {"mode": "replace", "verbs": verbs}

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def sync_window_size(master_fd):
    """Copy the real terminal's window size to the PTY master."""
    try:
        size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\x00" * 8)
        fcntl.ioctl(master_fd, termios.TIOCSWINSZ, size)
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Launch Claude Code with custom crab colors")
    parser.add_argument(
        "--body",
        default=None,
        help="Body color as R,G,B or #hex (default: YC orange #FF6600)",
    )
    parser.add_argument(
        "--eyes",
        default=None,
        help="Eye color as R,G,B or #hex (default: unchanged)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to pack directory (reads colors from pack.json)",
    )
    parser.add_argument(
        "--verbs",
        default=None,
        help="Pack name or path to load verbs from (e.g. looksmaxxing, stripe)",
    )
    args, claude_args = parser.parse_known_args()

    # Apply verbs from a different pack if requested
    if args.verbs:
        verbs_dir = resolve_pack_dir(args.verbs)
        if verbs_dir:
            apply_verbs(verbs_dir)
        else:
            print(f"Warning: verb pack '{args.verbs}' not found, skipping", file=sys.stderr)

    # Resolve colors
    if args.config:
        body_rgb, eyes_rgb = load_pack_colors(args.config)
    else:
        body_rgb = parse_rgb(args.body) if args.body else (255, 102, 0)
        eyes_rgb = parse_rgb(args.eyes) if args.eyes else None

    color_filter = build_filter(body_rgb, eyes_rgb)

    # Build claude command — everything we didn't recognize goes to claude
    claude_cmd = ["claude"] + claude_args

    # ── PTY spawn with output filtering ────────────────────────────────
    # pty.fork() handles setsid/TIOCSCTTY/dup2 correctly on macOS.
    # We set window size immediately after fork, then SIGWINCH the child
    # so claude/Ink re-reads the correct terminal dimensions.

    pid, master_fd = pty.fork()

    if pid == 0:
        # Child: exec claude
        os.environ.setdefault("TERM", "xterm-256color")
        os.execvp(claude_cmd[0], claude_cmd)
        sys.exit(1)

    # Parent: set correct PTY size and tell child to re-read it
    sync_window_size(master_fd)
    import time
    time.sleep(0.05)  # let child start before SIGWINCH
    try:
        os.kill(pid, signal.SIGWINCH)
    except OSError:
        pass

    # Handle SIGWINCH (terminal resize) — propagate to PTY
    def handle_winch(signum, frame):
        sync_window_size(master_fd)
        os.kill(pid, signal.SIGWINCH)

    signal.signal(signal.SIGWINCH, handle_winch)

    # Put stdin in raw mode so keypresses pass through immediately
    old_tty = termios.tcgetattr(sys.stdin)
    try:
        import tty

        tty.setraw(sys.stdin)

        # I/O relay loop
        import select

        while True:
            try:
                rlist, _, _ = select.select([sys.stdin, master_fd], [], [], 0.1)
            except (select.error, ValueError):
                break

            if master_fd in rlist:
                try:
                    data = os.read(master_fd, 65536)
                except OSError:
                    break
                if not data:
                    break
                # Coalesce: grab any immediately available data to avoid
                # color codes splitting across chunk boundaries
                while True:
                    ready, _, _ = select.select([master_fd], [], [], 0)
                    if not ready:
                        break
                    try:
                        more = os.read(master_fd, 65536)
                    except OSError:
                        break
                    if not more:
                        break
                    data += more
                # Apply color filter
                filtered = color_filter(data)
                if filtered:
                    os.write(sys.stdout.fileno(), filtered)

            if sys.stdin in rlist:
                try:
                    data = os.read(sys.stdin.fileno(), 4096)
                except OSError:
                    break
                if not data:
                    break
                # Strip terminal ID responses from stdin before they
                # enter the PTY and get echoed back to the screen
                data = re.sub(
                    rb"\x1bP[^\x1b]*\x1b\\|\x1b\[\?[0-9;]*c",
                    b"",
                    data,
                )
                if data:
                    os.write(master_fd, data)



    finally:
        # Restore terminal
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

    # Wait for child and exit with its status
    _, status = os.waitpid(pid, 0)
    sys.exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)


if __name__ == "__main__":
    main()
