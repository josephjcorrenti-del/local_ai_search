from email.message import Message

import pytest

from local_search import web_page


class FakeResponse:
    def __init__(
        self,
        body: bytes,
        *,
        url: str = "https://example.com/page",
        content_type: str = "text/html; charset=utf-8",
    ) -> None:
        self.body = body
        self.url = url
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def geturl(self) -> str:
        return self.url

    def read(self, size: int = -1) -> bytes:
        return self.body if size < 0 else self.body[:size]


def test_web_page_fetch_returns_normalized_page(monkeypatch) -> None:
    monkeypatch.setattr(
        web_page,
        "urlopen",
        lambda request, timeout: FakeResponse(
            b"""
            <html>
              <head><title>Example Page</title></head>
              <body>
                <p>Current information.</p>
                <script>ignored()</script>
              </body>
            </html>
            """
        ),
    )

    result = web_page.web_page_fetch(
        "https://example.com/page"
    )

    assert result["url"] == "https://example.com/page"
    assert result["title"] == "Example Page"
    assert "Current information." in result["content_text"]
    assert "ignored()" not in result["content_text"]
    assert result["fetched_at"]


def test_web_page_fetch_accepts_plain_text(monkeypatch) -> None:
    monkeypatch.setattr(
        web_page,
        "urlopen",
        lambda request, timeout: FakeResponse(
            b"plain text content",
            content_type="text/plain",
        ),
    )

    result = web_page.web_page_fetch(
        "https://example.com/page"
    )

    assert result["title"] is None
    assert result["content_text"] == "plain text content"


def test_web_page_fetch_rejects_invalid_scheme() -> None:
    with pytest.raises(ValueError, match="http or https"):
        web_page.web_page_fetch("file:///tmp/private.txt")


def test_web_page_fetch_bounds_response_size(monkeypatch) -> None:
    monkeypatch.setattr(
        web_page,
        "urlopen",
        lambda request, timeout: FakeResponse(b"x" * 11),
    )

    with pytest.raises(RuntimeError, match="exceeds 10 bytes"):
        web_page.web_page_fetch(
            "https://example.com/page",
            max_bytes=10,
        )


def test_web_page_fetch_rejects_unsupported_content(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        web_page,
        "urlopen",
        lambda request, timeout: FakeResponse(
            b"%PDF",
            content_type="application/pdf",
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="unsupported web content type",
    ):
        web_page.web_page_fetch(
            "https://example.com/file.pdf"
        )
