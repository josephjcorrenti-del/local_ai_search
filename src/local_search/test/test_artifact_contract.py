import json
from pathlib import Path

from local_search.ingest import web_artifact_index
from local_search.storage import schema_init, search_get


def test_minimal_web_artifact_with_content_text_indexes(tmp_path: Path) -> None:
    schema_init()

    artifact_path = tmp_path / "minimal_artifact.json"
    artifact_path.write_text(
        json.dumps(
            {
                "content_text": "minimal artifact contract alpha bravo",
            }
        ),
        encoding="utf-8",
    )

    result = web_artifact_index(artifact_path)

    assert result["status"] == "indexed"

    results = search_get("alpha", limit=10)

    assert len(results) >= 1
    assert results[0]["source_type"] == "web_artifact"


def test_web_search_results_artifact_indexes_result_items(tmp_path: Path) -> None:
    schema_init()

    artifact_path = tmp_path / "search_results_artifact.json"
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_type": "web_search_results",
                "provider": "test",
                "query": "fallout release date",
                "title": "Search results for fallout release date",
                "content_text": "Fallout 3 release date October 28 2008",
                "results": [
                    {
                        "title": "Fallout 3",
                        "url": "https://example.test/fallout-3",
                        "snippet": "Fallout 3 was released on October 28, 2008.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = web_artifact_index(artifact_path)

    assert result["status"] == "indexed"

    results = search_get("released October", limit=10)

    assert len(results) >= 1
    assert results[0]["source_type"] == "web_artifact"
    assert results[0]["title"] == "Fallout 3"
    assert results[0]["url"] == "https://example.test/fallout-3"
    assert "released" in results[0]["snippet"].lower()
