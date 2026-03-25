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
import signal
import struct
import sys
import fcntl
import termios

# ── Original Clawd colors (consistent across CC versions) ──────────────
ORIGINAL_BODY = b"38;2;215;119;87"  # clawd_body: rgb(215,119,87)
ORIGINAL_BG = b"48;2;0;0;0"  # clawd_background: rgb(0,0,0)

# Also match if clawd_body appears as background (some edge rendering)
ORIGINAL_BODY_AS_BG = b"48;2;215;119;87"


def make_replacement(r, g, b):
    """Build the replacement byte string for a color."""
    return f"{r};{g};{b}".encode()


def build_filter(body_rgb, bg_rgb=None):
    """Return a function that replaces clawd colors in an ANSI byte stream."""
    new_body_fg = b"38;2;" + make_replacement(*body_rgb)
    new_body_bg = b"48;2;" + make_replacement(*body_rgb)

    replacements = [
        (ORIGINAL_BODY, new_body_fg),
        (ORIGINAL_BODY_AS_BG, new_body_bg),
    ]

    if bg_rgb:
        new_bg = b"48;2;" + make_replacement(*bg_rgb)
        replacements.append((ORIGINAL_BG, new_bg))

    def apply(data):
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
    """Load body color from a vibescc pack.json."""
    pack_json = os.path.join(pack_dir, "pack.json")
    with open(pack_json) as f:
        pack = json.load(f)
    primary = pack["colors"]["primary"]
    return parse_rgb(primary)


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
        "--bg",
        default=None,
        help="Background/eye color as R,G,B or #hex (default: unchanged)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to pack directory (reads colors from pack.json)",
    )
    parser.add_argument(
        "claude_args",
        nargs="*",
        help="Additional arguments passed to claude",
    )

    args = parser.parse_args()

    # Resolve colors
    if args.config:
        body_rgb = load_pack_colors(args.config)
    elif args.body:
        body_rgb = parse_rgb(args.body)
    else:
        body_rgb = (255, 102, 0)  # YC orange default

    bg_rgb = parse_rgb(args.bg) if args.bg else None

    color_filter = build_filter(body_rgb, bg_rgb)

    # Build claude command
    claude_cmd = ["claude"] + args.claude_args

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
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                # Apply color filter to output
                filtered = color_filter(data)
                os.write(sys.stdout.fileno(), filtered)

            if sys.stdin in rlist:
                try:
                    data = os.read(sys.stdin.fileno(), 4096)
                except OSError:
                    break
                if not data:
                    break
                os.write(master_fd, data)

    finally:
        # Restore terminal
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

    # Wait for child and exit with its status
    _, status = os.waitpid(pid, 0)
    sys.exit(os.WEXITSTATUS(status) if os.WIFEXITED(status) else 1)


if __name__ == "__main__":
    main()
