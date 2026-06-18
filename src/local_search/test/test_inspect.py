from pathlib import Path

from local_search.cli import index_file_command
from local_search.storage import document_inspect_get
from local_search.storage import search_get
from local_search.storage import schema_init


def test_document_inspect_returns_document_and_chunks(tmp_path: Path) -> None:
    schema_init()

    sample = tmp_path / "sample.txt"
    sample.write_text(
        f"inspect document test content echo foxtrot {tmp_path}\n",
        encoding="utf-8",
    )

    index_file_command(str(sample))

    results = search_get("foxtrot", limit=10)
    document_id = results[0]["document_id"]

    inspected = document_inspect_get(document_id)

    assert inspected is not None
    assert inspected["document"]["document_id"] == document_id
    assert inspected["document"]["source_type"] == "file"
    assert inspected["document"]["index_path"] == str(sample.resolve())
    assert len(inspected["chunks"]) == 1
    assert inspected["chunks"][0]["chunk_index"] == 0
