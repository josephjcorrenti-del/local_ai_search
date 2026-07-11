from __future__ import annotations

from typing import Any

from local_ai.memory import sessions_stats_get
from local_ai.workspace import workspace_load, workspace_names_get


def build_navigation_tree() -> dict[str, Any]:
    return {
        "sessions": _session_nodes(),
        "workspaces": [
            _workspace_node(name)
            for name in workspace_names_get()
        ],
    }


def _session_nodes() -> list[dict[str, str]]:
    sessions = sessions_stats_get()

    sessions.sort(
        key=lambda item: (
            str(item.get("last_updated") or ""),
            str(item.get("session") or "").lower(),
        ),
        reverse=True,
    )

    return [
        {"name": str(item["session"])}
        for item in sessions
        if item.get("session")
    ]


def _workspace_node(name: str) -> dict[str, Any]:
    workspace = workspace_load(name)

    return {
        "name": name,
        "sessions": [
            {"name": session_name}
            for session_name in workspace.get("sessions", [])
        ],
        "files": [
            {"path": path}
            for path in workspace.get("files", [])
        ],
    }
