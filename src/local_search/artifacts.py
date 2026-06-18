"""Artifact loading helpers for local_search."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def artifact_load(path: Path) -> dict[str, Any]:
    """Load and validate a local_search artifact JSON object."""
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid artifact JSON: {path}") from exc

    if not isinstance(artifact, dict):
        raise ValueError(
            f"artifact root must be a JSON object: {path}"
        )

    return artifact
