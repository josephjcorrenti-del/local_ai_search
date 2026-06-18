from pathlib import Path

from local_search.cli import index_file_command
from local_search.storage import schema_init, search_get


def test_search_result_contract(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        "contract test alpha bravo\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("alpha", limit=1)

    assert len(results) == 1

    result = results[0]

    expected_keys = {
        "document_id",
        "source_id",
        "raw_ref",
        "chunk_id",
        "source_type",
        "index_path",
        "url",
        "title",
        "score",
        "snippet",
        "chunk_index",
        "rank"
    }

    assert set(result.keys()) == expected_keys

    assert isinstance(result["document_id"], str)
    assert isinstance(result["source_id"], str)
    assert isinstance(result["raw_ref"], str)
    assert isinstance(result["chunk_id"], str)
    assert isinstance(result["source_type"], str)
    assert isinstance(result["index_path"], str)
    assert isinstance(result["score"], float)
    assert isinstance(result["snippet"], str)
    assert isinstance(result["chunk_index"], int)
    assert isinstance(result["rank"], int)
    assert result["rank"] == 1