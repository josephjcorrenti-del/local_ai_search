from __future__ import annotations

from pathlib import Path

from local_ai_search.config import load_config


def filesystem_config_get():
    return load_config().filesystem


def path_should_include(path: Path) -> bool:
    config = filesystem_config_get()

    if path.name in config.ignored_filenames:
        return False

    if path.suffix in config.ignored_extensions:
        return False

    if path.suffix not in config.supported_extensions:
        return False

    if any(part in config.ignored_directories for part in path.parts):
        return False

    return True
