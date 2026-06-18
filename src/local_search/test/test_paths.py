from local_search.paths import DATA_ROOT
from local_search.paths import DB_PATH


def test_data_root_name() -> None:
    assert DATA_ROOT.name == "local_search"


def test_db_name() -> None:
    assert DB_PATH.name == "search.db"
