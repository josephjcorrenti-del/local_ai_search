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


@pytest.fixture(autouse=True)
def disable_live_web_search(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCAL_SEARCH_DISABLE_NETWORK", "1")