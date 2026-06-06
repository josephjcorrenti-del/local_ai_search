import json

from local_ai_search.logging import log_event
from local_ai_search.paths import get_paths


def test_log_event_writes_ndjson(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "local_ai_search.paths.get_repo_root",
        lambda: tmp_path,
    )

    log_event(
        "test.event",
        command="test",
        event_outcome="success",
        elapsed_ms=12,
    )

    paths = get_paths()
    lines = paths.run_log.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

    payload = json.loads(lines[0])

    assert payload["event"] == "test.event"
    assert payload["message"] == "test.event"
    assert payload["level"] == "INFO"
    assert payload["params"]["command"] == "test"
    assert payload["event_outcome"] == "success"
    assert payload["elapsed_ms"] == 12
    assert "ts" in payload
    assert "run_id" in payload


def test_log_event_verbose_stdout(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "local_ai_search.paths.get_repo_root",
        lambda: tmp_path,
    )
    monkeypatch.setenv("LOCAL_AI_SEARCH_VERBOSE", "1")

    log_event("test.verbose", command="test")

    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["event"] == "test.verbose"
    assert payload["params"]["command"] == "test"
