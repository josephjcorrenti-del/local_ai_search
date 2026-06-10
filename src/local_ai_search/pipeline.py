from __future__ import annotations

from typing import Any


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