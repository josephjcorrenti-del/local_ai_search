from __future__ import annotations

"""
local_ai/fs.py

Explicit file system access layer.

Responsibilities:
- Read a single file (explicit, no scanning)
- Validate path exists and is a file
- Provide:
  - bounded read for inspection (fs_read)
  - question-aware content selection (fs_content_window_get)

Design notes:
- Read-only
- No recursion, no directory traversal
- One-shot access only
- Logging mirrors web.py lifecycle
"""

from pathlib import Path
import time
from typing import Any

from local_ai.config import CONFIG
from local_ai.log import log_event
from local_ai.content_window import content_window_get


# -----------------------------
# Core validation helper
# -----------------------------
def _validate_file_path(path: str) -> Path:
    path_obj = Path(path)

    if not path_obj.exists():
        raise RuntimeError(f"path does not exist: {path}")

    if not path_obj.is_file():
        raise RuntimeError(f"path is not a file: {path}")

    return path_obj


# -----------------------------
# Bounded read (for read-file)
# -----------------------------
def fs_read(path: str, max_chars: int | None = None) -> dict[str, Any]:
    """Read a file and return bounded content for inspection."""
    path_str = str(path)

    log_event("fs.read.start", path=path_str)
    started_at = time.perf_counter()

    try:
        path_obj = _validate_file_path(path)

        if max_chars is None:
            max_chars = CONFIG.web_chat_max_source_chars

        content = path_obj.read_text(encoding="utf-8", errors="replace")
        size = len(content)

        included = content[:max_chars]
        truncated = size > len(included)

        result = {
            "path": str(path_obj),
            "size": size,
            "content": included,
            "included_chars": len(included),
            "truncated": truncated,
        }

        log_event(
            "fs.read.ready",
            path=path_str,
            event_outcome="success",
            elapsed_ms=int((time.perf_counter() - started_at) * 1000),
        )

        return result

    except Exception as exc:
        log_event(
            "fs.read.error",
            level="ERROR",
            path=path_str,
            error=str(exc),
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
        )
        raise


# -----------------------------
# Question-aware windowing (for file-chat)
# -----------------------------
def fs_content_window_get(
    path: str,
    question: str,
    max_chars: int,
) -> dict[str, Any]:
    """
    Read a file and return question-aware bounded content.

    Flow:
    - read full file (one-time explicit access)
    - apply bag-of-words window selection
    - return bounded content for AI prompt
    """
    path_str = str(path)

    log_event("fs.read.start", path=path_str)
    started_at = time.perf_counter()

    try:
        path_obj = _validate_file_path(path)

        content = path_obj.read_text(encoding="utf-8", errors="replace")
        size = len(content)

        window = content_window_get(
            content,
            max_chars,
            question=question,
        )

        result = {
            "path": str(path_obj),
            "size": size,
            **window,
        }

        log_event(
            "fs.read.ready",
            path=path_str,
            event_outcome="success",
            elapsed_ms=int((time.perf_counter() - started_at) * 1000),
        )

        return result

    except Exception as exc:
        log_event(
            "fs.read.error",
            level="ERROR",
            path=path_str,
            error=str(exc),
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
        )
        raise


def path_resolve_user_input(path: str) -> Path:
    return Path(path).expanduser().resolve()