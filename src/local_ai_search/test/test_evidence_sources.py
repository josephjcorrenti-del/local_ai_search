import pytest

from local_ai_search.evidence_sources import (
    EVIDENCE_SOURCE_TYPES,
    evidence_source_type_validate,
)


def test_evidence_source_types_are_defined():
    assert EVIDENCE_SOURCE_TYPES == (
        "workspace",
        "session",
        "file",
        "web_artifact",
        "search_result",
        "model_knowledge",
    )


def test_evidence_source_type_validate_accepts_supported_values():
    for source_type in EVIDENCE_SOURCE_TYPES:
        assert evidence_source_type_validate(source_type) == source_type


def test_evidence_source_type_validate_rejects_unknown_values():
    with pytest.raises(ValueError) as exc:
        evidence_source_type_validate("project")

    assert "unsupported evidence source type" in str(exc.value)