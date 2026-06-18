"""Retrieval shaping helpers for local_search."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from local_search.config import RETRIEVAL_VERSION
from local_search.artifacts import artifact_load

def _text_cap(text: str, max_chars: int) -> str:
    """Return text bounded to max_chars."""
    if max_chars <= 0:
        return ""

    if len(text) <= max_chars:
        return text

    return text[: max_chars - 3].rstrip() + "..."


def artifact_evidence_get(
    artifact_path: Path,
    *,
    limit: int = 5,
    max_chars: int = 4000,
) -> dict[str, Any]:
    """Return an AI-ready evidence package from a saved web search artifact."""
    artifact = artifact_load(artifact_path)

    results = artifact.get("results")
    if not isinstance(results, list):
        results = []

    evidence_results: list[dict[str, Any]] = []
    remaining_chars = max_chars

    for rank, result in enumerate(results[:limit], start=1):
        title = str(result.get("title") or "").strip()
        url = str(result.get("url") or "").strip()
        snippet = str(result.get("snippet") or "").strip()

        if not title and not url and not snippet:
            continue

        snippet = _text_cap(snippet, remaining_chars)

        evidence_results.append(
            {
                "rank": rank,
                "title": title,
                "url": url,
                "snippet": snippet,
            }
        )

        remaining_chars -= len(title) + len(url) + len(snippet)

        if remaining_chars <= 0:
            break

    return {
        "retrieval_version": RETRIEVAL_VERSION,
        "artifact_type": artifact.get("artifact_type"),
        "query": artifact.get("query"),
        "provider": artifact.get("provider"),
        "fetched_at": artifact.get("fetched_at"),
        "results": evidence_results,
    }
