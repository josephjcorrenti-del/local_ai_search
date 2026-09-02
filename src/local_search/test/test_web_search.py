import pytest

from local_search.web_search import (
    WebSearchDisabledError,
    provider_url_validate,
    web_search,
)


def test_provider_url_validate_accepts_http() -> None:
    result = provider_url_validate("http://localhost:8080")

    assert result == "http://localhost:8080"


def test_provider_url_validate_accepts_https_and_removes_trailing_slash() -> None:
    result = provider_url_validate("https://search.example.com/")

    assert result == "https://search.example.com"


@pytest.mark.parametrize(
    "base_url",
    [
        "",
        "   ",
        "file:///tmp/search",
        "ftp://example.com",
        "/search",
        "localhost:8080",
        "http://",
    ],
)
def test_provider_url_validate_rejects_invalid_urls(base_url: str) -> None:
    with pytest.raises(ValueError):
        provider_url_validate(base_url)


def test_web_search_rejects_network_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LOCAL_SEARCH_DISABLE_NETWORK", "1")

    with pytest.raises(
        WebSearchDisabledError,
        match="external web search is disabled",
    ):
        web_search("this must not reach SearXNG")