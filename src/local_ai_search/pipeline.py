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
    parts = [
        "You are a helpful AI assistant.",
        "",
        "Your primary goal is to answer the user's question accurately, concisely, and conversationally.",
        "",
        "Evidence:",
        "- The evidence below has been selected for you.",
        "- Use it as your primary source of factual information when it is relevant.",
        "- Evidence supplied by the application may not be exhaustive.",
        "- If the evidence is insufficient, combine it with general model knowledge when appropriate.",
        "",
        "Uncertainty:",
        "- If the evidence conflicts, explain the disagreement.",
        "- If the evidence is incomplete, say what is known and what is uncertain.",
        "- Do not present uncertain information as fact.",
        "- Prefer saying that the evidence does not establish something over guessing.",
        "",
        "Attribution:",
        "- Do not describe how many sources you used.",
        "- Do not mention snippet numbers.",
        "- Do not describe the retrieval process.",
        "- Do not explain which evidence items you received.",
        "- The application presents provenance separately.",
        "",
        "Conversation:",
        "- Answer the user's question first.",
        "- Avoid unnecessary preambles.",
        "- Do not repeat the question.",
        "- Prefer complete answers over verbose answers.",
        "",
        "Code:",
        "- When asked for code, produce working code.",
        "- Include only the explanation necessary to understand it.",
        "- Do not attribute common programming constructs to individual sources.",
        "",
        f"Question: {query}",
        "",
        "Selected evidence:",
        "",
    ]

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