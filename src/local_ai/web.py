from __future__ import annotations

"""
local_ai/web.py

Explicit web access layer for fetching and storing web content.

Responsibilities:
- Fetch content from a single explicit URL
- Extract and normalize basic text content from HTML
- Persist fetched content as inspectable JSON artifacts
- Provide cleanup of old web artifacts

Design notes:
- Web access is opt-in and explicit (no automatic browsing)
- Each fetch produces a stored artifact under app data root
- Content extraction is simple and lossy (text-focused, no DOM structure)
- Artifacts are designed to be inspectable and reusable
- Logging traces fetch lifecycle and file operations, not content
"""

import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, UTC
from pathlib import Path
from typing import Any

from local_ai.log import log_event
from local_ai.paths import paths_get
from local_ai.content_window import content_window_get
from local_search.web_page import web_page_fetch


def web_timestamp_now_get() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def web_artifact_id_get(url: str) -> str:
    """Return a stable artifact identifier for the given URL."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]


def web_artifact_path_get(url: str) -> str:
    """Return the artifact file path for the given URL."""
    artifact_id = web_artifact_id_get(url)
    web_dir = paths_get().web_dir
    web_dir.mkdir(parents=True, exist_ok=True)
    return str(web_dir / f"{artifact_id}.json")


# WHY:
# Web fetch is explicit and artifact-based. Every fetch both returns content
# and writes an inspectable JSON snapshot so later commands can reason over
# the same stored input rather than hidden in-memory state.
def web_fetch(url: str) -> dict[str, Any]:
    """Fetch one URL, store its artifact, and return the artifact data."""
    log_event(
        "web.fetch.start",
        url=url,
    )

    started_at = time.perf_counter()

    try:
        artifact = web_page_fetch(
            url,
            user_agent="local_ai/0.1",
        )
    except (RuntimeError, ValueError) as exc:
        log_event(
            "web.fetch.error",
            level="error",
            url=url,
            error=str(exc),
            event_outcome="failure",
        )
        raise RuntimeError(f"Failed to fetch URL: {url}") from exc

    artifact_path = web_artifact_path_get(artifact["url"])

    log_event(
        "web.artifact.save",
        path=artifact_path,
        url=artifact["url"],
    )

    with open(artifact_path, "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, indent=2)

    artifact["artifact_path"] = artifact_path

    log_event(
        "web.fetch.ready",
        path=artifact_path,
        url=artifact["url"],
        event_outcome="success",
        elapsed_ms=int(
            (time.perf_counter() - started_at) * 1000
        ),
    )

    return artifact


def web_search(query: str, limit: int = 3) -> list[dict[str, Any]]:
    """Search the web and fetch top results as artifacts."""
    log_event("web.search.start", url=query)

    search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"

    req = urllib.request.Request(
        search_url,
        headers={"User-Agent": "local_ai/0.1"},
        method="GET",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")

    debug_path = paths_get().web_dir / "search_debug.html"
    debug_path.write_text(html, encoding="utf-8")

    raw_links = re.findall(
        r'href="[^"]*uddg=([^"&]+)',
        html,
    )

    links = []
    for encoded in raw_links:
        url = urllib.parse.unquote(encoded)

        # basic sanity filter
        if url.startswith("http"):
            links.append(url)

    results = []
    seen = set()

    for url in links:
        if url in seen:
            continue
        seen.add(url)

        try:
            artifact = web_fetch(url)
            results.append(artifact)
        except Exception:
            continue

        if len(results) >= limit:
            break

    log_event("web.search.ready", url=query)

    return results


def web_artifact_load(path: str) -> dict[str, Any]:
    """Load a saved web artifact from disk."""
    log_event(
        "web.artifact.load",
        path=path,
    )

    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def web_artifact_content_window_get(
    artifact: dict[str, Any],
    max_chars: int,
    question: str | None = None,
) -> dict[str, Any]:
    """Return bounded source content metadata for prompt construction."""
    return content_window_get(
        artifact.get("content_text", ""),
        max_chars,
        question,
    )


def web_cleanup(days: int, delete: bool) -> list[Path]:
    """Find or remove web artifacts older than the given age."""
    paths = paths_get()
    web_dir = paths.web_dir

    log_event(
        "web.cleanup.start",
        path=str(web_dir),
    )

    started_at = time.perf_counter()

    if not web_dir.exists():
        log_event(
            "web.cleanup.skip_missing_dir",
            path=str(web_dir),
        )
        return []

    cutoff = datetime.now(UTC) - timedelta(days=days)

    removed: list[Path] = []

    for file_path in web_dir.glob("*.json"):
        try:
            stat = file_path.stat()
            modified = datetime.fromtimestamp(stat.st_mtime, UTC)
        except OSError:
            continue

        if modified < cutoff:
            removed.append(file_path)
            if delete:
                try:
                    file_path.unlink()
                    log_event(
                        "web.artifact.delete",
                        path=str(file_path),
                    )
                except OSError:
                    pass

    log_event(
        "web.cleanup.ready",
        path=str(web_dir),
        event_outcome="success",
        elapsed_ms=int((time.perf_counter() - started_at) * 1000),
    )

    return removed


