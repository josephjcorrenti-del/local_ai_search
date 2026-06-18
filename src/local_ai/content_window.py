from __future__ import annotations

"""
local_ai/content_window.py

Shared text windowing for bounded prompt construction.

Responsibilities:
- Split large text into overlapping windows
- Score windows against an optional question
- Return bounded content metadata for prompt construction

Design notes:
- Pure text logic only
- No file, web, artifact, or model ownership
- No side effects
"""

import re
from typing import Any


CONTENT_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "i", "in", "is", "it", "of", "on", "or", "that", "the",
    "this", "to", "what", "when", "where", "which", "who", "why",
    "with",
}


def content_terms_get(text: str) -> set[str]:
    """Return simple lowercase terms for bag-of-words matching."""
    terms = set()

    for term in re.findall(r"[a-zA-Z0-9_]+", text.lower()):
        if len(term) < 3:
            continue
        if term in CONTENT_STOP_WORDS:
            continue
        terms.add(term)

    return terms


def content_windows_get(
    text: str,
    window_chars: int = 2000,
    overlap_chars: int = 300,
) -> list[str]:
    """Split text into overlapping character windows."""
    if not text:
        return []

    windows = []
    start = 0

    while start < len(text):
        end = min(start + window_chars, len(text))
        windows.append(text[start:end])

        if end >= len(text):
            break

        start = max(end - overlap_chars, start + 1)

    return windows


def content_window_score(question_terms: set[str], window: str) -> int:
    """Score a text window using simple bag-of-words overlap."""
    window_terms = content_terms_get(window)
    return len(question_terms & window_terms)


def content_window_get(
    text: str,
    max_chars: int,
    question: str | None = None,
) -> dict[str, Any]:
    """Return bounded content metadata for prompt construction."""
    if not question:
        bounded_content = text[:max_chars]
    else:
        question_terms = content_terms_get(question)
        windows = content_windows_get(text)

        scored_windows = [
            (content_window_score(question_terms, window), index, window)
            for index, window in enumerate(windows)
        ]

        scored_windows.sort(key=lambda item: (-item[0], item[1]))

        separator = "\n\n---\n\n"

        selected_parts = []
        selected_chars = 0

        for score, _index, window in scored_windows:
            if score <= 0:
                continue

            separator_chars = len(separator) if selected_parts else 0
            remaining = max_chars - selected_chars - separator_chars

            if remaining <= 0:
                break

            selected = window[:remaining]
            selected_parts.append(selected)
            selected_chars += separator_chars + len(selected)

        bounded_content = separator.join(selected_parts)

        if not bounded_content:
            bounded_content = text[:max_chars]

    return {
        "content_text": bounded_content,
        "included_chars": len(bounded_content),
        "total_chars": len(text),
        "truncated": len(text) > len(bounded_content),
    }
