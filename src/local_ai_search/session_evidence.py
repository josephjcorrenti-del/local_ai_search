from __future__ import annotations

from typing import Any

from local_ai.memory import session_load, session_turns_get


def build_session_evidence(session_name: str | None) -> dict[str, Any]:
    turns = session_turns_get(session_name)
    session = session_load(session_name)

    results: list[dict[str, Any]] = []

    summary = session.get("summary")
    if isinstance(summary, dict) and summary.get("text"):
        results.append(
            {
                "rank": len(results) + 1,
                "title": f"Session summary: {session.get('session')}",
                "url": "",
                "snippet": summary["text"],
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
        "session": session.get("session"),
        "results": results,
    }
