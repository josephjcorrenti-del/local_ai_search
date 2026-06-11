from __future__ import annotations

from typing import Any

from local_ai_search.adapters import local_ai

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