from local_search.paths import APP_NAME, DATA_ROOT, DB_PATH, REPO_ROOT


def test_data_root_name() -> None:
    assert DATA_ROOT.name == "local_search"


def test_db_name() -> None:
    assert DB_PATH.name == "search.db"

    assert DATA_ROOT == REPO_ROOT / "data" / APP_NAME