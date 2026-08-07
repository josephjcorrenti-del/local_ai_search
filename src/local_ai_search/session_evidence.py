from __future__ import annotations

from typing import Any

from local_ai.memory import session_context_get


def build_session_evidence(session_name: str | None) -> dict[str, Any]:
    context = session_context_get(session_name)
    turns = context["turns"]
    summary = context["summary"]

    results: list[dict[str, Any]] = []

    if isinstance(summary, str) and summary.strip():
        results.append(
            {
                "rank": len(results) + 1,
                "title": f"Session summary: {session_name}",
                "url": None,
                "snippet": summary,
                "source_type": "session",
            }
        )

    for turn in turns:
        results.append(
            {
                "rank": len(results) + 1,
                "title": f"Session {turn['role']}",
                "url": "",
                "snippet": turn["content"],
                "source_type": "session",
            }
        )

    return {
        "retrieval_version": 1,
        "artifact_type": "session_context",
        "provider": "local_ai",
        "query": None,
        "session": context["session"],
        "results": results,
    }
