import pytest

from local_search.web_search import provider_url_validate


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
