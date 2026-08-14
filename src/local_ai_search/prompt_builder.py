from __future__ import annotations

from pathlib import Path
from typing import Any


from local_ai_search.adapters import local_ai
from local_ai_search.config import EVIDENCE_LIMIT, EVIDENCE_MAX_CHARS
from local_ai_search.evidence import load_evidence_from_local_search

def build_prompt(
    query: str,
    evidence: dict[str, Any],
    session_name: str | None = None,
) -> str:
    del session_name
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
        "Uncertainty and competing evidence:",
        "- Compare the evidence items for agreement, disagreement, and missing detail before answering.",
        "- When evidence conflicts, describe the competing claims and the disagreement explicitly.",
        "- Do not silently choose one conflicting claim.",
        "- If one claim is better supported, explain why and qualify the conclusion.",
        "- When evidence is incomplete, separate what is established, what is uncertain, and what information is missing.",
        '- Use clear language such as "the evidence suggests," "the sources disagree," or "the available evidence does not establish this."',
        "- Do not present uncertain information as fact.",
        "- Prefer acknowledging uncertainty over guessing.",
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

    parts.append(f"Current question: {query}")

    return "\n".join(parts).rstrip()


def run_query(
    query: str,
    evidence: dict,
    session_name: str | None = None,
) -> str:
    orchestrator_context = build_prompt(
        query,
        evidence,
        session_name=session_name,
    )

    return local_ai.chat(
        query,
        session_name=session_name,
        orchestrator_context=orchestrator_context,
    )


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