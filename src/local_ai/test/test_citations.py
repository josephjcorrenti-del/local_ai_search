from local_ai.citations import (
    citation_ranks_get,
    citation_validation_get,
)


def test_citation_ranks_get_returns_single_reference():
    assert citation_ranks_get("SQLite is embedded [1].") == (1,)


def test_citation_ranks_get_returns_multiple_references():
    assert citation_ranks_get("SQLite and DuckDB are embedded [1][3].") == (1, 3)


def test_citation_validation_accepts_allowed_references():
    result = citation_validation_get(
        "SQLite and DuckDB are embedded [1][3].",
        {1, 2, 3},
        citation_required=True,
    )

    assert result.valid is True
    assert result.citation_missing is False
    assert result.invalid_ranks == ()


def test_citation_validation_rejects_missing_reference():
    result = citation_validation_get(
        "SQLite is embedded.",
        {1},
        citation_required=True,
    )

    assert result.valid is False
    assert result.citation_missing is True


def test_citation_validation_rejects_unknown_reference():
    result = citation_validation_get(
        "SQLite is embedded [4].",
        {1, 2, 3},
        citation_required=True,
    )

    assert result.valid is False
    assert result.invalid_ranks == (4,)


def test_citation_validation_allows_uncited_answer_when_not_required():
    result = citation_validation_get(
        "Hello there.",
        set(),
        citation_required=False,
    )

    assert result.valid is True
    assert result.citation_missing is False


def test_citation_validation_treats_combined_reference_as_missing():
    result = citation_validation_get(
        "SQLite and DuckDB are embedded [1, 3].",
        {1, 3},
        citation_required=True,
    )

    assert result.valid is False
    assert result.citation_missing is True
