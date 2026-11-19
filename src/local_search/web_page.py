"""Bounded retrieval of one explicit web page."""

from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_BYTES = 1_000_000


def web_url_validate(url: str) -> str:
    candidate = url.strip()
    parsed = urlparse(candidate)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("web URL must use http or https")

    if not parsed.hostname:
        raise ValueError("web URL must include a hostname")

    return candidate


def html_title_get(html_text: str) -> str | None:
    match = re.search(
        r"<title[^>]*>(.*?)</title>",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return None

    title = unescape(match.group(1)).strip()
    title = re.sub(r"\s+", " ", title)
    return title or None


def html_text_extract(html_text: str) -> str:
    text = re.sub(
        r"(?is)<script[^>]*>.*?</script>",
        " ",
        html_text,
    )
    text = re.sub(
        r"(?is)<style[^>]*>.*?</style>",
        " ",
        text,
    )
    text = re.sub(
        r"(?is)<noscript[^>]*>.*?</noscript>",
        " ",
        text,
    )

    text = re.sub(
        r"(?i)<(p|div|h[1-6]|li|section|article)[^>]*>",
        "\n",
        text,
    )
    text = re.sub(
        r"(?i)</(p|div|h[1-6]|li|section|article)>",
        "\n",
        text,
    )
    text = re.sub(r"(?i)<br[^>]*>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = unescape(text)

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.split("\n")
    ]
    lines = [line for line in lines if line]

    seen: set[str] = set()
    deduplicated: list[str] = []

    for line in lines:
        if line in seen:
            continue

        seen.add(line)
        deduplicated.append(line)

    return "\n".join(deduplicated)


def web_page_fetch(
    url: str,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
    user_agent: str = "local_search/0.1",
) -> dict[str, Any]:
    """Fetch one bounded HTML or plain-text web page."""
    validated_url = web_url_validate(url)

    request = Request(
        validated_url,
        headers={
            "User-Agent": user_agent,
            "Accept": "text/html,text/plain;q=0.9",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            final_url = web_url_validate(response.geturl())
            content_type = response.headers.get(
                "Content-Type",
                "",
            )
            raw_bytes = response.read(max_bytes + 1)
    except HTTPError as exc:
        raise RuntimeError(
            f"failed to fetch URL with HTTP {exc.code}: {validated_url}"
        ) from exc
    except URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(
            f"failed to fetch URL: {validated_url}: {reason}"
        ) from exc
    except OSError as exc:
        raise RuntimeError(
            f"failed to fetch URL: {validated_url}: {exc}"
        ) from exc

    if len(raw_bytes) > max_bytes:
        raise RuntimeError(
            f"web response exceeds {max_bytes} bytes: {final_url}"
        )

    media_type = content_type.split(";", 1)[0].strip().lower()

    if media_type not in {"text/html", "text/plain"}:
        raise RuntimeError(
            f"unsupported web content type "
            f"{media_type or 'unknown'}: {final_url}"
        )

    decoded_text = raw_bytes.decode("utf-8", errors="replace")

    if media_type == "text/html":
        title = html_title_get(decoded_text)
        content_text = html_text_extract(decoded_text)
    else:
        title = None
        content_text = decoded_text.strip()

    if not content_text:
        raise RuntimeError(
            f"web page contains no usable text: {final_url}"
        )

    return {
        "url": final_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "content_type": content_type,
        "title": title,
        "content_text": content_text,
    }
