"""Provider-neutral external search result contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from urllib.parse import urlparse


SearchProviderOutcome = Literal[
    "results",
    "zero_results",
    "rate_limited",
    "quota_exhausted",
    "provider_failure",
    "unavailable",
]

SEARCH_PROVIDER_OUTCOMES = frozenset(
    {
        "results",
        "zero_results",
        "rate_limited",
        "quota_exhausted",
        "provider_failure",
        "unavailable",
    }
)

_SUCCESS_OUTCOMES = frozenset(
    {
        "results",
        "zero_results",
    }
)

_FAILURE_OUTCOMES = SEARCH_PROVIDER_OUTCOMES - _SUCCESS_OUTCOMES


@dataclass(frozen=True)
class SearchProviderResult:
    """One normalized result returned by an external search provider."""

    title: str
    url: str
    snippet: str

    def __post_init__(self) -> None:
        if not isinstance(self.title, str):
            raise ValueError("search result title must be a string")

        if not isinstance(self.url, str) or not self.url.strip():
            raise ValueError("search result URL must be a non-empty string")

        if not isinstance(self.snippet, str):
            raise ValueError("search result snippet must be a string")

        parsed_url = urlparse(self.url)

        if parsed_url.scheme not in {"http", "https"}:
            raise ValueError(
                "search result URL must use http or https"
            )

        if not parsed_url.hostname:
            raise ValueError(
                "search result URL must include a hostname"
            )

        if not self.title.strip() and not self.snippet.strip():
            raise ValueError(
                "search result must include a title or snippet"
            )


@dataclass(frozen=True)
class SearchProviderResponse:
    """Normalized result of one external provider request."""

    provider: str
    query: str
    outcome: SearchProviderOutcome
    results: tuple[SearchProviderResult, ...] = ()
    error_code: str | None = None
    message: str | None = None
    retry_after_seconds: int | None = None
    quota_remaining: int | None = None
    quota_reset_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError(
                "search provider must be a non-empty string"
            )

        if not isinstance(self.query, str) or not self.query.strip():
            raise ValueError(
                "search query must be a non-empty string"
            )

        if self.outcome not in SEARCH_PROVIDER_OUTCOMES:
            raise ValueError(
                f"unsupported search provider outcome: {self.outcome}"
            )

        if not isinstance(self.results, tuple):
            raise ValueError(
                "search provider results must be a tuple"
            )

        if not all(
            isinstance(result, SearchProviderResult)
            for result in self.results
        ):
            raise ValueError(
                "search provider results must use SearchProviderResult"
            )

        if self.outcome == "results" and not self.results:
            raise ValueError(
                "results outcome requires at least one result"
            )

        if self.outcome != "results" and self.results:
            raise ValueError(
                f"{self.outcome} outcome cannot include results"
            )

        if self.outcome in _SUCCESS_OUTCOMES:
            if self.error_code is not None:
                raise ValueError(
                    "successful outcomes cannot include an error code"
                )

            if self.message is not None:
                raise ValueError(
                    "successful outcomes cannot include an error message"
                )

            if self.retry_after_seconds is not None:
                raise ValueError(
                    "successful outcomes cannot include retry timing"
                )

        if self.outcome in _FAILURE_OUTCOMES:
            if not self.error_code and not self.message:
                raise ValueError(
                    f"{self.outcome} outcome requires failure details"
                )

        if self.error_code is not None and not isinstance(
            self.error_code,
            str,
        ):
            raise ValueError(
                "search provider error code must be a string"
            )

        if self.message is not None and not isinstance(
            self.message,
            str,
        ):
            raise ValueError(
                "search provider message must be a string"
            )

        if self.retry_after_seconds is not None:
            if (
                isinstance(self.retry_after_seconds, bool)
                or not isinstance(self.retry_after_seconds, int)
                or self.retry_after_seconds < 0
            ):
                raise ValueError(
                    "retry_after_seconds must be a nonnegative integer"
                )

        if self.quota_remaining is not None:
            if (
                isinstance(self.quota_remaining, bool)
                or not isinstance(self.quota_remaining, int)
                or self.quota_remaining < 0
            ):
                raise ValueError(
                    "quota_remaining must be a nonnegative integer"
                )

        if self.quota_reset_at is not None:
            if not isinstance(self.quota_reset_at, datetime):
                raise ValueError(
                    "quota_reset_at must be a datetime"
                )

            if (
                self.quota_reset_at.tzinfo is None
                or self.quota_reset_at.utcoffset() is None
            ):
                raise ValueError(
                    "quota_reset_at must include timezone information"
                )
