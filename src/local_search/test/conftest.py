from collections.abc import Iterator

import pytest

from local_search.paths import DB_PATH


@pytest.fixture(autouse=True)
def clean_search_db() -> Iterator[None]:
    if DB_PATH.exists():
        DB_PATH.unlink()

    yield

    if DB_PATH.exists():
        DB_PATH.unlink()