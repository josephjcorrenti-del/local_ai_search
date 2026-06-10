from __future__ import annotations

import subprocess

from local_ai_search.adapters import local_ai


def test_ask_runs_local_ai_prompt(monkeypatch):
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
            stdout="answer text\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert local_ai.ask("question text") == "answer text"
    assert calls == [
        {
            "command": ["local-ai", "prompt", "question text"],
            "check": False,
            "capture_output": True,
            "text": True,
        }
    ]


def test_ask_raises_on_failure(monkeypatch):
    def fake_run(command, *, check, capture_output, text):
        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="model failed\n",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    try:
        local_ai.ask("question text")
    except RuntimeError as exc:
        assert str(exc) == "model failed"
    else:
        raise AssertionError("expected RuntimeError")
