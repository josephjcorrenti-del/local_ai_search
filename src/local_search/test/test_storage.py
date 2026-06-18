from pathlib import Path

from local_search.config import SCHEMA_VERSION
from local_search.storage import (
    counts_get,
    fts5_available_check,
    schema_init,
    schema_version_get,
)


def test_schema_init_creates_database(tmp_path: Path) -> None:
    db_path = tmp_path / "search.db"

    schema_init(db_path)

    assert db_path.exists()
    assert schema_version_get(db_path) == SCHEMA_VERSION


def test_schema_init_creates_empty_counts(tmp_path: Path) -> None:
    db_path = tmp_path / "search.db"

    schema_init(db_path)

    assert counts_get(db_path) == {
        "sources": 0,
        "documents": 0,
        "chunks": 0,
    }


def test_fts5_available() -> None:
    assert fts5_available_check() is True
