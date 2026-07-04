from __future__ import annotations

from pathlib import Path

from local_ai_search.filesystem_policy import (
    filesystem_config_get,
    path_should_include,
)


def walk_filesystem(root: str | Path) -> list[str]:
    root_path = Path(root).expanduser().resolve()

    if not root_path.exists():
        raise ValueError(f"filesystem root does not exist: {root_path}")

    if not root_path.is_dir():
        raise ValueError(f"filesystem root is not a directory: {root_path}")

    config = filesystem_config_get()

    results: list[str] = []

    for path in sorted(root_path.rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root_path)

        if not path_should_include(relative_path):
            continue

        results.append(relative_path.as_posix())

        if len(results) >= config.max_files:
            break

    return results
