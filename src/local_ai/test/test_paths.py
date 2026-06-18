from __future__ import annotations

from pathlib import Path

from local_ai.paths import paths_get


def test_paths_default_data_root():
    paths = paths_get()

    expected_data_root = Path.home() / "ai" / "data"
    expected_app_data_root = expected_data_root / "local_ai"

    assert paths.data_root == expected_data_root
    assert paths.app_data_root == expected_app_data_root
    assert paths.sessions_dir == expected_app_data_root / "sessions"
    assert paths.web_dir == expected_app_data_root / "web"


def test_repo_paths_resolve_consistently():
    paths = paths_get()

    assert paths.src_root == paths.repo_root / "src"
    assert paths.package_root == paths.src_root / "local_ai"
    assert paths.scripts_dir == paths.repo_root / "scripts"
