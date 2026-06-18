from __future__ import annotations

"""Text helpers for local_search."""

import hashlib


def sha256_hex(text: str) -> str:
    """Return SHA256 hex digest for text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_text(
    text: str,
    *,
    chunk_size: int = 1200,
    chunk_overlap: int = 200,
) -> list[dict]:
    """Split text into overlapping character chunks."""
    chunks: list[dict] = []

    if not text.strip():
        return chunks

    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        content = text[start:end]

        chunks.append(
            {
                "chunk_index": chunk_index,
                "content": content,
                "start_char": start,
                "end_char": end,
            }
        )

        if end >= len(text):
            break

        start += chunk_size - chunk_overlap
        chunk_index += 1

    return chunks


def chunk_snippet_build(
    content: str,
    query: str,
    *,
    max_chars: int = 280,
) -> str:
    """Build a readable snippet from chunk content around the first query term."""
    normalized_content = " ".join(content.split())

    if not normalized_content:
        return ""

    query_terms = [
        term.lower()
        for term in query.split()
        if term.strip()
    ]

    lowered = normalized_content.lower()

    match_index = -1
    for term in query_terms:
        match_index = lowered.find(term)
        if match_index >= 0:
            break

    if match_index < 0:
        return normalized_content[:max_chars]

    half = max_chars // 2
    start = max(match_index - half, 0)
    end = min(start + max_chars, len(normalized_content))

    snippet = normalized_content[start:end]

    if start > 0:
        snippet = f"...{snippet}"

    if end < len(normalized_content):
        snippet = f"{snippet}..."

    return snippet