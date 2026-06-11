from __future__ import annotations

from pathlib import Path
from typing import Any


from local_ai_search.adapters import local_ai
from local_ai_search.config import EVIDENCE_LIMIT, EVIDENCE_MAX_CHARS
from local_ai_search.evidence import load_evidence_from_local_search

def build_prompt(
    query: str,
    evidence: dict[str, Any],
) -> str:
    parts = [f"Question: {query}", "", "Evidence:", ""]

    for result in evidence.get("results", []):
        parts.append(f"[{result['rank']}] {result['title']}")
        parts.append(f"URL: {result['url']}")
        parts.append("Snippet:")
        parts.append(result["snippet"])
        parts.append("")

    return "\n".join(parts).rstrip()

def run_query(query: str, evidence: dict) -> str:
    prompt = build_prompt(query, evidence)
    return local_ai.ask(prompt)


def run_query_from_evidence_path(
    query: str,
    evidence_path: str,
    *,
    limit: int = EVIDENCE_LIMIT,
    max_chars: int = EVIDENCE_MAX_CHARS,
) -> str:
    evidence = load_evidence_from_local_search(
        Path(evidence_path),
        limit=limit,
        max_chars=max_chars,
    )
    return run_query(query, evidence)