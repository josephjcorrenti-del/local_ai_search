import json
from pathlib import Path

from local_search.retrieval import artifact_evidence_get


def test_artifact_evidence_get_returns_ai_ready_package(tmp_path: Path) -> None:
    artifact_path = tmp_path / "web_search.json"
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_type": "web_search_results",
                "query": "coffee maker cost",
                "provider": "searxng",
                "fetched_at": "2026-05-19T07:45:43-04:00",
                "results": [
                    {
                        "title": "Coffee Makers - Target",
                        "url": "https://example.test/target",
                        "snippet": "Coffee makers by price under $25 under $50 under $100.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    evidence = artifact_evidence_get(artifact_path)

    assert evidence["artifact_type"] == "web_search_results"
    assert evidence["query"] == "coffee maker cost"
    assert evidence["provider"] == "searxng"
    assert evidence["fetched_at"] == "2026-05-19T07:45:43-04:00"
    assert evidence["retrieval_version"] == 1

    assert evidence["results"] == [
        {
            "rank": 1,
            "title": "Coffee Makers - Target",
            "url": "https://example.test/target",
            "snippet": "Coffee makers by price under $25 under $50 under $100.",
        }
    ]


def test_artifact_evidence_get_respects_limit(tmp_path: Path) -> None:
    artifact_path = tmp_path / "web_search.json"
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_type": "web_search_results",
                "query": "puppy facts",
                "provider": "searxng",
                "fetched_at": "2026-05-19T18:58:53-04:00",
                "results": [
                    {"title": "one", "url": "https://one.test", "snippet": "one"},
                    {"title": "two", "url": "https://two.test", "snippet": "two"},
                ],
            }
        ),
        encoding="utf-8",
    )

    evidence = artifact_evidence_get(artifact_path, limit=1)

    assert len(evidence["results"]) == 1
    assert evidence["results"][0]["rank"] == 1
    assert evidence["results"][0]["title"] == "one"


def test_artifact_evidence_get_bounds_snippet_text(tmp_path: Path) -> None:
    artifact_path = tmp_path / "web_search.json"
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_type": "web_search_results",
                "query": "long snippet",
                "provider": "searxng",
                "fetched_at": "2026-05-19T18:58:53-04:00",
                "results": [
                    {
                        "title": "long",
                        "url": "https://long.test",
                        "snippet": "alpha " * 100,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    evidence = artifact_evidence_get(artifact_path, max_chars=40)

    assert len(evidence["results"][0]["snippet"]) <= 40
    assert evidence["results"][0]["snippet"].endswith("...")


def test_artifact_evidence_contract(tmp_path: Path) -> None:
    artifact_path = tmp_path / "web_search.json"
    artifact_path.write_text(
        json.dumps(
            {
                "artifact_type": "web_search_results",
                "query": "contract query",
                "provider": "searxng",
                "fetched_at": "2026-05-19T18:58:53-04:00",
                "results": [
                    {
                        "title": "Contract Result",
                        "url": "https://example.test/contract",
                        "snippet": "contract snippet",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    evidence = artifact_evidence_get(artifact_path)

    expected_keys = {
        "retrieval_version",
        "artifact_type",
        "query",
        "provider",
        "fetched_at",
        "results",
    }

    assert set(evidence.keys()) == expected_keys
    assert isinstance(evidence["retrieval_version"], int)
    assert isinstance(evidence["artifact_type"], str)
    assert isinstance(evidence["query"], str)
    assert isinstance(evidence["provider"], str)
    assert isinstance(evidence["fetched_at"], str)
    assert isinstance(evidence["results"], list)

    result = evidence["results"][0]

    expected_result_keys = {
        "rank",
        "title",
        "url",
        "snippet",
    }

    assert set(result.keys()) == expected_result_keys
    assert isinstance(result["rank"], int)
    assert isinstance(result["title"], str)
    assert isinstance(result["url"], str)
    assert isinstance(result["snippet"], str)