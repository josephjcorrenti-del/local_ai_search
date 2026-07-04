from __future__ import annotations

from pathlib import Path
from typing import Any

from local_ai_search.filesystem_policy import path_should_include
from local_ai_search.filesystem_walk import walk_filesystem


def _path_under_root(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _append_file_result(
    results: list[dict[str, Any]],
    *,
    relative_path: str,
    content: str,
) -> None:
    results.append(
        {
            "rank": len(results) + 1,
            "title": f"File: {relative_path}",
            "url": "",
            "snippet": content,
            "source_type": "file",
        }
    )


def build_filesystem_evidence(
    root: str | Path,
    *,
    files: list[str] | None = None,
    max_chars_per_file: int = 4000,
) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()

    results: list[dict[str, Any]] = []

    if files is None:
        files = walk_filesystem(root_path)

    for relative_path in sorted(files):
        candidate = (root_path / relative_path).resolve()

        if not _path_under_root(root_path, candidate):
            raise ValueError(f"path is outside filesystem evidence root: {relative_path}")

        if not path_should_include(Path(relative_path)):
            continue

        if not candidate.is_file():
            continue

        content = candidate.read_text(encoding="utf-8")[:max_chars_per_file]

        _append_file_result(
            results,
            relative_path=relative_path,
            content=content,
        )

    return {
        "retrieval_version": 1,
        "artifact_type": "filesystem_context",
        "provider": "filesystem",
        "query": None,
        "root": str(root_path),
        "results": results,
    }
