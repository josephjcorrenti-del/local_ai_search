from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from local_ai_search.adapters.local_search import LocalSearchAdapterError
from local_search.paths import ARTIFACTS_DIR


def query_slug(query: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", query.strip().lower())
    return slug.strip("_")


def latest_web_artifact_for_query(query: str) -> Path:
    pattern = f"search_{query_slug(query)}_*.json"
    web_artifacts_dir = ARTIFACTS_DIR / "web"
    matches = sorted(web_artifacts_dir.glob(pattern))

    if not matches:
        raise LocalSearchAdapterError(
            f"no web artifact found for query: {query}"
        )

    return matches[-1]


def artifact_fetched_at_get(path: Path) -> datetime:
    """Return an artifact's timezone-aware retrieval timestamp."""
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LocalSearchAdapterError(
            f"cannot read cached web artifact: {path}"
        ) from exc

    fetched_at_value = artifact.get("fetched_at")

    if not isinstance(fetched_at_value, str):
        raise LocalSearchAdapterError(
            f"cached web artifact has no valid fetched_at: {path}"
        )

    try:
        fetched_at = datetime.fromisoformat(fetched_at_value)
    except ValueError as exc:
        raise LocalSearchAdapterError(
            f"cached web artifact has no valid fetched_at: {path}"
        ) from exc

    if fetched_at.tzinfo is None or fetched_at.utcoffset() is None:
        raise LocalSearchAdapterError(
            f"cached web artifact fetched_at has no timezone: {path}"
        )

    return fetched_at


def fresh_web_artifact_validate(
    artifact_path: Path,
    *,
    max_age_seconds: int,
    now: datetime | None = None,
) -> Path:
    """Return an artifact path when its retrieval timestamp is fresh."""
    fetched_at = artifact_fetched_at_get(artifact_path)
    checked_at = now or datetime.now(timezone.utc)

    if checked_at.tzinfo is None or checked_at.utcoffset() is None:
        raise ValueError("now must include timezone information")

    age_seconds = (
        checked_at.astimezone(timezone.utc)
        - fetched_at.astimezone(timezone.utc)
    ).total_seconds()

    if age_seconds < 0:
        raise LocalSearchAdapterError(
            f"cached web artifact is future-dated: {artifact_path}"
        )

    if age_seconds > max_age_seconds:
        raise LocalSearchAdapterError(
            f"cached web artifact is stale: {artifact_path}"
        )

    return artifact_path


def latest_fresh_web_artifact_for_query(
    query: str,
    *,
    max_age_seconds: int,
    now: datetime | None = None,
) -> Path:
    """Return the newest exact-query artifact when it is still fresh."""
    return fresh_web_artifact_validate(
        latest_web_artifact_for_query(query),
        max_age_seconds=max_age_seconds,
        now=now,
    )


def first_fresh_related_web_artifact(
    results: list[dict[str, Any]],
    *,
    max_age_seconds: int,
    now: datetime | None = None,
) -> Path:
    """Return the highest-ranked fresh web artifact from FTS results."""
    seen_paths: set[Path] = set()

    for result in results:
        if result.get("source_type") != "web_artifact":
            continue

        raw_ref = result.get("raw_ref")
        if not isinstance(raw_ref, str) or not raw_ref.strip():
            continue

        artifact_path = Path(raw_ref).resolve()

        if artifact_path in seen_paths:
            continue

        seen_paths.add(artifact_path)

        try:
            return fresh_web_artifact_validate(
                artifact_path,
                max_age_seconds=max_age_seconds,
                now=now,
            )
        except LocalSearchAdapterError:
            continue

    raise LocalSearchAdapterError(
        "no fresh related web artifact found"
    )