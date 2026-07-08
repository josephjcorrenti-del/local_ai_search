from __future__ import annotations

from typing import Any

from local_ai.memory import session_names_get
from local_ai.workspace import workspace_load, workspace_names_get


def build_navigation_tree() -> dict[str, Any]:
    return {
        "sessions": [
            {"name": name}
            for name in session_names_get()
        ],
        "workspaces": [
            _workspace_node(name)
            for name in workspace_names_get()
        ],
    }


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
