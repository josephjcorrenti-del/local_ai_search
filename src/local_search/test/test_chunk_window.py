from pathlib import Path

from local_search.cli import index_file_command
from local_search.storage import chunk_window_get
from local_search.storage import schema_init
from local_search.storage import search_get


def test_chunk_window_get_returns_current_and_neighboring_chunks(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        ("alpha " * 250)
        + ("target bravo " * 120)
        + ("charlie " * 250),
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("target", limit=1)

    document_id = results[0]["document_id"]
    chunk_index = results[0]["chunk_index"]

    window = chunk_window_get(document_id, chunk_index, radius=1)

    assert len(window) >= 1
    assert any(chunk["chunk_index"] == chunk_index for chunk in window)
    assert window == sorted(window, key=lambda chunk: chunk["chunk_index"])


def test_chunk_window_get_bounds_at_first_chunk(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        "target " + ("alpha " * 500),
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("target", limit=1)

    window = chunk_window_get(
        results[0]["document_id"],
        results[0]["chunk_index"],
        radius=2,
    )

    assert window[0]["chunk_index"] == 0
