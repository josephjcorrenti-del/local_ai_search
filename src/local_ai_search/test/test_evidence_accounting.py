import pytest

from local_ai_search.evidence_accounting import (
    EvidenceCounts,
    evidence_counts_from_results,
)


def test_evidence_counts_as_dict():
    counts = EvidenceCounts(
        available_count=32,
        evidence_count=5,
        displayed_count=10,
    )

    assert counts.as_dict() == {
        "available_count": 32,
        "evidence_count": 5,
        "displayed_count": 10,
    }


def test_evidence_counts_from_results():
    counts = evidence_counts_from_results(
        available_count=32,
        evidence_count=5,
        displayed_count=10,
    )

    assert counts.available_count == 32
    assert counts.evidence_count == 5
    assert counts.displayed_count == 10


@pytest.mark.parametrize(
    "kwargs",
    [
        {"available_count": -1, "evidence_count": 0, "displayed_count": 0},
        {"available_count": 0, "evidence_count": -1, "displayed_count": 0},
        {"available_count": 0, "evidence_count": 0, "displayed_count": -1},
    ],
)


def test_evidence_counts_reject_negative_values(kwargs):
    with pytest.raises(ValueError):
        evidence_counts_from_results(**kwargs)


def test_available_count_from_artifact(tmp_path):
    from local_ai_search.evidence_accounting import available_count_from_artifact

    artifact = tmp_path / "artifact.json"
    artifact.write_text(
        """
        {
          "results": [
            {"title": "one"},
            {"title": "two"},
            {"title": "three"}
          ]
        }
        """,
        encoding="utf-8",
    )

    assert available_count_from_artifact(artifact) == 3


def test_evidence_counts_for_web_artifact(tmp_path):
    from local_ai_search.evidence_accounting import evidence_counts_for_web_artifact

    artifact = tmp_path / "artifact.json"
    artifact.write_text(
        """
        {
          "results": [
            {"title": "one"},
            {"title": "two"},
            {"title": "three"}
          ]
        }
        """,
        encoding="utf-8",
    )

    evidence = {
        "results": [
            {"title": "one"},
            {"title": "two"},
        ]
    }

    counts = evidence_counts_for_web_artifact(
        artifact,
        evidence,
        displayed_limit=1,
    )

    assert counts.as_dict() == {
        "available_count": 3,
        "evidence_count": 2,
        "displayed_count": 1,
    }
