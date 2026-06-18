from pathlib import Path

from local_search.cli import index_file_command
from local_search.storage import counts_get, schema_init


def test_index_file_adds_source_document_and_chunk(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text("local search engines are cool\nsqlite fts5 is useful\n", encoding="utf-8")

    result = index_file_command(str(sample))

    assert result == 0

    counts = counts_get()
    assert counts["sources"] >= 1
    assert counts["documents"] >= 1
    assert counts["chunks"] >= 1


def test_index_file_skips_unchanged_file(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text("unchanged content\n", encoding="utf-8")

    first = index_file_command(str(sample))
    before = counts_get()

    second = index_file_command(str(sample))
    after = counts_get()

    assert first == 0
    assert second == 0
    assert after == before
