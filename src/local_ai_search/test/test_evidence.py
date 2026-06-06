import pytest

from local_ai_search.evidence import (
    EvidenceError,
    evidence_char_count,
    format_evidence_preview,
    validate_evidence,
)


def good_evidence():
    return {
        "retrieval_version": 1,
        "artifact_type": "web_search_results",
        "query": "antique shops",
        "provider": "searxng",
        "fetched_at": "2026-05-23T08:51:04.605674-04:00",
        "results": [
            {
                "rank": 1,
                "title": "Example Result",
                "url": "https://example.com",
                "snippet": "Example snippet.",
            }
        ],
    }


def test_validate_good_evidence():
    validate_evidence(good_evidence(), max_chars=4000)


def test_validate_rejects_missing_retrieval_version():
    evidence = good_evidence()
    del evidence["retrieval_version"]

    with pytest.raises(EvidenceError, match="missing required evidence field"):
        validate_evidence(evidence)


def test_validate_rejects_unsupported_retrieval_version():
    evidence = good_evidence()
    evidence["retrieval_version"] = 999

    with pytest.raises(EvidenceError, match="unsupported retrieval_version"):
        validate_evidence(evidence)


def test_validate_rejects_missing_required_field():
    evidence = good_evidence()
    del evidence["provider"]

    with pytest.raises(EvidenceError, match="missing required evidence field"):
        validate_evidence(evidence)


def test_validate_rejects_results_not_list():
    evidence = good_evidence()
    evidence["results"] = {}

    with pytest.raises(EvidenceError, match="results must be a list"):
        validate_evidence(evidence)


def test_validate_rejects_result_missing_field():
    evidence = good_evidence()
    del evidence["results"][0]["snippet"]

    with pytest.raises(EvidenceError, match="missing field: snippet"):
        validate_evidence(evidence)


def test_validate_rejects_over_max_chars():
    evidence = good_evidence()

    with pytest.raises(EvidenceError, match="exceeds max chars"):
        validate_evidence(evidence, max_chars=1)


def test_evidence_char_count_counts_title_url_and_snippet():
    evidence = good_evidence()

    assert evidence_char_count(evidence) == (
        len("Example Result") + len("https://example.com") + len("Example snippet.")
    )


def test_format_evidence_preview():
    preview = format_evidence_preview(good_evidence())

    assert "query: antique shops" in preview
    assert "provider: searxng" in preview
    assert "retrieval_version: 1" in preview
    assert "[1] Example Result" in preview
    assert "https://example.com" in preview
    assert "Example snippet." in preview
