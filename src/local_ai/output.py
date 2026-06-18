from __future__ import annotations

"""
local_ai/output.py

Human-facing CLI output helpers.

Responsibilities:
- Terminal presentation (color, symbols, formatting)
- Small, explicit helpers for success/failure/warning messages

Non-responsibilities:
- No structured logging; use log.py
- No business logic
- No hidden behavior

Design rule:
- Anything printed for humans belongs here or in command-specific CLI output.
- Anything structured for machines belongs in log.py.
"""

import sys
import os

USE_COLOR = sys.stdout.isatty() or os.environ.get("OWB_FORCE_COLOR") == "1"


def color_green(text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[32m{text}\033[0m"


def color_red(text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[31m{text}\033[0m"


def color_yellow(text: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[33m{text}\033[0m"


def ok(message: str) -> None:
    print(f"{color_green('[✓]')} {message}")


def fail(message: str) -> None:
    print(f"{color_red('[✗]')} {message}", file=sys.stderr)


def warn(message: str) -> None:
    print(f"{color_yellow('[!]')} {message}")


def info(message: str) -> None:
    print(f"[*] {message}")
