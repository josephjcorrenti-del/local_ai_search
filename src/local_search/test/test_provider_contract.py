from datetime import datetime, timezone

import pytest

from local_search.provider_contract import (
    SearchProviderResponse,
    SearchProviderResult,
)


def valid_result() -> SearchProviderResult:
    return SearchProviderResult(
        title="Python",
        url="https://www.python.org/",
        snippet="The Python programming language.",
    )


def test_provider_response_accepts_results() -> None:
    response = SearchProviderResponse(
        provider="test",
        query="Python programming language",
        outcome="results",
        results=(valid_result(),),
        quota_remaining=99,
        quota_reset_at=datetime(
            2026,
            11,
            19,
            tzinfo=timezone.utc,
        ),
    )

    assert response.outcome == "results"
    assert response.results == (valid_result(),)
    assert response.quota_remaining == 99


def test_provider_response_accepts_genuine_zero_results() -> None:
    response = SearchProviderResponse(
        provider="test",
        query="query with no results",
        outcome="zero_results",
    )

    assert response.outcome == "zero_results"
    assert response.results == ()


@pytest.mark.parametrize(
    "outcome",
    [
        "rate_limited",
        "quota_exhausted",
        "provider_failure",
        "unavailable",
    ],
)
def test_provider_response_accepts_failure_outcomes(
    outcome,
) -> None:
    response = SearchProviderResponse(
        provider="test",
        query="Python",
        outcome=outcome,
        error_code="test_error",
        message="Provider could not complete the request.",
        retry_after_seconds=60,
    )

    assert response.outcome == outcome
    assert response.results == ()


def test_provider_result_rejects_non_web_url() -> None:
    with pytest.raises(
        ValueError,
        match="must use http or https",
    ):
        SearchProviderResult(
            title="Local file",
            url="file:///tmp/result.txt",
            snippet="Not a web result.",
        )


def test_provider_result_requires_title_or_snippet() -> None:
    with pytest.raises(
        ValueError,
        match="title or snippet",
    ):
        SearchProviderResult(
            title="",
            url="https://example.com/",
            snippet="",
        )


def test_results_outcome_requires_results() -> None:
    with pytest.raises(
        ValueError,
        match="requires at least one result",
    ):
        SearchProviderResponse(
            provider="test",
            query="Python",
            outcome="results",
        )


def test_non_results_outcome_rejects_results() -> None:
    with pytest.raises(
        ValueError,
        match="cannot include results",
    ):
        SearchProviderResponse(
            provider="test",
            query="Python",
            outcome="zero_results",
            results=(valid_result(),),
        )


def test_success_outcome_rejects_failure_details() -> None:
    with pytest.raises(
        ValueError,
        match="cannot include an error code",
    ):
        SearchProviderResponse(
            provider="test",
            query="Python",
            outcome="zero_results",
            error_code="unexpected",
        )


def test_failure_outcome_requires_details() -> None:
    with pytest.raises(
        ValueError,
        match="requires failure details",
    ):
        SearchProviderResponse(
            provider="test",
            query="Python",
            outcome="provider_failure",
        )


@pytest.mark.parametrize(
    "field,value,error",
    [
        (
            "retry_after_seconds",
            -1,
            "retry_after_seconds",
        ),
        (
            "quota_remaining",
            -1,
            "quota_remaining",
        ),
    ],
)
def test_provider_response_rejects_negative_metadata(
    field,
    value,
    error,
) -> None:
    arguments = {
        "provider": "test",
        "query": "Python",
        "outcome": "provider_failure",
        "message": "Temporary failure.",
        field: value,
    }

    with pytest.raises(ValueError, match=error):
        SearchProviderResponse(**arguments)


def test_quota_reset_requires_timezone() -> None:
    with pytest.raises(
        ValueError,
        match="must include timezone",
    ):
        SearchProviderResponse(
            provider="test",
            query="Python",
            outcome="quota_exhausted",
            message="Monthly quota exhausted.",
            quota_reset_at=datetime(2026, 12, 1),
        )


def test_provider_response_rejects_unknown_outcome() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported search provider outcome",
    ):
        SearchProviderResponse(
            provider="test",
            query="Python",
            outcome="surprise",  # type: ignore[arg-type]
            message="Unknown state.",
        )
