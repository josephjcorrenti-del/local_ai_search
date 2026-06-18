import json
from pathlib import Path

import pytest

from local_search.artifacts import artifact_load


def test_artifact_load_accepts_json_object(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.json"

    artifact_path.write_text(
        json.dumps({"query": "coffee"}),
        encoding="utf-8",
    )

    artifact = artifact_load(artifact_path)

    assert artifact["query"] == "coffee"


def test_artifact_load_rejects_invalid_json(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.json"

    artifact_path.write_text(
        '{"query": ',
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        artifact_load(artifact_path)


def test_artifact_load_rejects_non_object_json(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.json"

    artifact_path.write_text(
        json.dumps(["not", "an", "object"]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        artifact_load(artifact_path)
