import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from local_ai_search import artifacts
from local_ai_search.artifacts import query_slug
from local_ai_search.adapters.local_search import LocalSearchAdapterError

def test_query_slug():
    assert query_slug("Jumping insects!") == "jumping_insects"


def artifact_write(path: Path, *, fetched_at: str) -> None:
    path.write_text(
        json.dumps({"fetched_at": fetched_at}),
        encoding="utf-8",
    )


def test_latest_fresh_web_artifact_returns_fresh_exact_match(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    web_dir = tmp_path / "web"
    web_dir.mkdir()

    artifact_path = (
        web_dir / "search_python_release_20261016070000.json"
    )
    artifact_write(
        artifact_path,
        fetched_at="2026-10-16T07:00:00-04:00",
    )

    monkeypatch.setattr(artifacts, "ARTIFACTS_DIR", tmp_path)

    result = artifacts.latest_fresh_web_artifact_for_query(
        "Python release",
        max_age_seconds=86400,
        now=datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc),
    )

    assert result == artifact_path


def test_latest_fresh_web_artifact_rejects_stale_match(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    web_dir = tmp_path / "web"
    web_dir.mkdir()

    artifact_path = (
        web_dir / "search_python_release_20261014070000.json"
    )
    artifact_write(
        artifact_path,
        fetched_at="2026-10-14T07:00:00-04:00",
    )

    monkeypatch.setattr(artifacts, "ARTIFACTS_DIR", tmp_path)

    with pytest.raises(LocalSearchAdapterError, match="is stale"):
        artifacts.latest_fresh_web_artifact_for_query(
            "Python release",
            max_age_seconds=86400,
            now=datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc),
        )


def test_latest_fresh_web_artifact_rejects_future_match(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    web_dir = tmp_path / "web"
    web_dir.mkdir()

    artifact_path = (
        web_dir / "search_python_release_20261017070000.json"
    )
    artifact_write(
        artifact_path,
        fetched_at="2026-10-17T07:00:00-04:00",
    )

    monkeypatch.setattr(artifacts, "ARTIFACTS_DIR", tmp_path)

    with pytest.raises(LocalSearchAdapterError, match="future-dated"):
        artifacts.latest_fresh_web_artifact_for_query(
            "Python release",
            max_age_seconds=86400,
            now=datetime(2026, 10, 16, 12, 0, tzinfo=timezone.utc),
        )


def test_related_artifact_selects_first_fresh_web_result(
    tmp_path,
) -> None:
    from datetime import datetime, timezone
    import json

    from local_ai_search.artifacts import (
        first_fresh_related_web_artifact,
    )

    stale_path = tmp_path / "stale.json"
    stale_path.write_text(
        json.dumps(
            {
                "fetched_at": "2026-10-24T12:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    fresh_path = tmp_path / "fresh.json"
    fresh_path.write_text(
        json.dumps(
            {
                "fetched_at": "2026-10-26T11:30:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    result = first_fresh_related_web_artifact(
        [
            {
                "source_type": "file",
                "raw_ref": str(fresh_path),
            },
            {
                "source_type": "web_artifact",
                "raw_ref": str(stale_path),
            },
            {
                "source_type": "web_artifact",
                "raw_ref": str(fresh_path),
            },
        ],
        max_age_seconds=86400,
        now=datetime(
            2026,
            10,
            26,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert result == fresh_path.resolve()