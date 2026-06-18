from pathlib import Path

from local_search.cli import index_file_command
from local_search.storage import schema_init, search_get


def test_search_returns_indexed_file(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        f"unique sqlite search test content alpha bravo {tmp_path}\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("alpha", limit=10)

    assert len(results) >= 1
    assert results[0]["source_type"] == "file"
    assert results[0]["index_path"] == str(sample.resolve())
    assert "alpha" in results[0]["snippet"].lower()
    assert "[" not in results[0]["snippet"]
    assert "]" not in results[0]["snippet"]


def test_search_missing_term_returns_empty_list(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        f"unique missing term test content charlie delta {tmp_path}\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("nonexistentterm", limit=10)

    assert results == []


def test_search_matches_reordered_terms(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        f"Pennsylvania trees include oak maple hemlock {tmp_path}\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("trees Pennsylvania", limit=10)

    assert len(results) >= 1
    assert results[0]["source_type"] == "file"
    assert results[0]["index_path"] == str(sample.resolve())
    assert "trees" in results[0]["snippet"].lower()


def test_search_handles_hyphenated_terms(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        f"x-men comic search content {tmp_path}\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("x-men", limit=10)

    assert len(results) >= 1


def test_search_ignores_common_stop_words(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        f"harrisburg population census data {tmp_path}\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("population of harrisburg", limit=10)

    assert len(results) >= 1
    assert results[0]["source_type"] == "file"
    assert results[0]["index_path"] == str(sample.resolve())