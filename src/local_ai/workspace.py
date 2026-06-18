from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from local_ai.paths import paths_get

def _append_unique(items: list[str], value: str) -> bool:
    if value in items:
        return False

    items.append(value)
    return True


def workspace_session_add(workspace_name: str, session_name: str) -> dict[str, Any]:
    data = workspace_load(workspace_name)
    changed = _append_unique(data["sessions"], session_name)

    if changed:
        workspace_save(workspace_name, data)

    return {
        "workspace": workspace_name,
        "session": session_name,
        "changed": changed,
    }


def _workspace_dir_get() -> Path:
    paths = paths_get()
    return paths.app_data_root / "workspaces"


def _workspace_path_get(name: str) -> Path:
    safe_name = workspace_name_validate(name)
    return _workspace_dir_get() / f"{safe_name}.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def workspace_create(name: str) -> dict[str, Any]:
    path = _workspace_path_get(name)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        raise RuntimeError(f"Workspace already exists: {name}")

    data: dict[str, Any] = {
        "name": name,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "sessions": [],
        "files": [],
        "web_artifacts": [],
        "notes": "",
    }

    path.write_text(json.dumps(data, indent=2))
    return data


def workspace_names_get() -> list[str]:
    root = _workspace_dir_get()
    if not root.exists():
        return []

    return sorted(p.stem for p in root.glob("*.json"))


def workspace_load(name: str) -> dict[str, Any]:
    path = _workspace_path_get(name)

    if not path.exists():
        raise RuntimeError(f"Workspace not found: {name}")

    data = json.loads(path.read_text())

    # minimal validation / defaults
    data.setdefault("sessions", [])
    data.setdefault("files", [])
    data.setdefault("web_artifacts", [])
    data.setdefault("notes", "")

    return data


def workspace_save(name: str, data: dict[str, Any]) -> None:
    path = _workspace_path_get(name)
    data["updated_at"] = _now_iso()
    path.write_text(json.dumps(data, indent=2))


def workspace_file_add(workspace_name: str, path: str) -> dict[str, Any]:
    data = workspace_load(workspace_name)
    changed = _append_unique(data["files"], path)

    if changed:
        workspace_save(workspace_name, data)

    return {
        "workspace": workspace_name,
        "file": path,
        "changed": changed,
    }


def workspace_web_artifact_add(
    workspace_name: str,
    artifact_path: str,
) -> dict[str, Any]:
    data = workspace_load(workspace_name)
    changed = _append_unique(data["web_artifacts"], artifact_path)

    if changed:
        workspace_save(workspace_name, data)

    return {
        "workspace": workspace_name,
        "web_artifact": artifact_path,
        "changed": changed,
    }


def workspace_chat_sources_get(workspace_name: str) -> dict[str, Any]:
    return workspace_load(workspace_name)


def workspace_name_validate(name: str) -> str:
    value = name.strip()

    if not value:
        raise ValueError("workspace name cannot be empty")

    if "/" in value or "\\" in value or ".." in value:
        raise ValueError("invalid workspace name")

    return value