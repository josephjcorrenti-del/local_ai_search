from __future__ import annotations

import subprocess

import pytest

from local_ai_search.adapters import local_search


def test_get_evidence_runs_local_search_evidence(monkeypatch):
    calls = []

    def fake_run(command, *, check, capture_output, text):
        calls.append(
            {
                "command": command,
                "check": check,
                "capture_output": capture_output,
                "text": text,
            }
        )
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout='{"retrieval_version": 1, "results": []}',
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    evidence = local_search.get_evidence("artifact.json", limit=3, max_chars=100)

    assert evidence == {"retrieval_version": 1, "results": []}
    assert calls == [
        {
            "command": [
                "local-search",
                "evidence",
                "artifact.json",
                "--limit",
                "3",
                "--max-chars",
                "100",
            ],
            "check": False,
            "capture_output": True,
            "text": True,
        }
    ]


def test_get_evidence_raises_on_failure(monkeypatch):
    def fake_run(command, *, check, capture_output, text):
        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="evidence failed\n",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(local_search.LocalSearchAdapterError) as exc:
        local_search.get_evidence("artifact.json")

    assert str(exc.value) == "evidence failed"


def test_get_evidence_raises_on_invalid_json(monkeypatch):
    def fake_run(command, *, check, capture_output, text):
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="not json",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(local_search.LocalSearchAdapterError) as exc:
        local_search.get_evidence("artifact.json")

    assert "invalid evidence JSON" in str(exc.value)
