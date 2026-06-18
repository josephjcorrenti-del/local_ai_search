"""CLI output helpers for local_search."""

from __future__ import annotations

import os


ANSI_GREEN = "\033[32m"
ANSI_RED = "\033[31m"
ANSI_BLUE = "\033[34m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"


def color_enabled() -> bool:
    """Return True if ANSI colors should be emitted."""
    return os.environ.get("NO_COLOR") is None


def _color(text: str, ansi: str) -> str:
    if not color_enabled():
        return text

    return f"{ansi}{text}{ANSI_RESET}"


def pass_print(message: str) -> None:
    print(_color(f"[✓] {message}", ANSI_GREEN))


def fail_print(message: str) -> None:
    print(_color(f"[x] {message}", ANSI_RED))


def info_print(message: str) -> None:
    print(_color(f"[*] {message}", ANSI_BLUE))


def debug_print(message: str) -> None:
    print(_color(f"[debug] {message}", ANSI_YELLOW))