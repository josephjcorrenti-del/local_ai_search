from local_ai_search.paths import APP_NAME, get_paths


def test_paths_are_repo_local():
    paths = get_paths()

    assert paths.repo_root.name == "local_ai_search"
    assert paths.data_root == paths.repo_root / "data" / APP_NAME
    assert paths.log_dir == paths.data_root / "logs"
    assert paths.run_log == paths.log_dir / "run.log"
    assert paths.evidence_dir == paths.data_root / "evidence"
    assert paths.exports_dir == paths.data_root / "exports"
