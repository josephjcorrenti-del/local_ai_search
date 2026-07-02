from __future__ import annotations

from typing import Any

from local_ai.workspace import workspace_chat_sources_get


def _append_result(
    results: list[dict[str, Any]],
    *,
    title: str,
    snippet: str,
) -> None:
    results.append(
        {
            "rank": len(results) + 1,
            "title": title,
            "url": "",
            "snippet": snippet,
            "source_type": "workspace",
        }
    )


def build_workspace_evidence(workspace_name: str) -> dict[str, Any]:
    workspace = workspace_chat_sources_get(workspace_name)

    results: list[dict[str, Any]] = []

    notes = workspace.get("notes")
    if isinstance(notes, str) and notes.strip():
        _append_result(
            results,
            title=f"Workspace notes: {workspace.get('name')}",
            snippet=notes,
        )

    for session_name in workspace.get("sessions", []):
        _append_result(
            results,
            title=f"Workspace session: {session_name}",
            snippet=session_name,
        )

    for path in workspace.get("files", []):
        _append_result(
            results,
            title=f"Workspace file: {path}",
            snippet=path,
        )

    for artifact_path in workspace.get("web_artifacts", []):
        _append_result(
            results,
            title=f"Workspace web artifact: {artifact_path}",
            snippet=artifact_path,
        )

    return {
        "retrieval_version": 1,
        "artifact_type": "workspace_context",
        "provider": "local_ai",
        "query": None,
        "workspace": workspace.get("name"),
        "results": results,
    }
