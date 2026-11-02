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


def test_ask_passes_session_persistence_metadata(monkeypatch):
    calls = []

    def fake_run(command, *, check, capture_output, text):
        calls.append(command)
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="answer text\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    answer = local_ai.ask(
        "evidence-aware prompt",
        session_name="api-test-session",
        user_content="question text",
    )

    assert answer == "answer text"
    assert calls == [
        [
            "local-ai",
            "prompt",
            "evidence-aware prompt",
            "--session",
            "api-test-session",
            "--user-content",
            "question text",
        ]
    ]


def test_chat_passes_session_and_orchestrator_context(
    monkeypatch,
):
    calls = []

    def fake_run(command, *, check, capture_output, text):
        calls.append(command)
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="answer text\n",
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    answer = local_ai.chat(
        "question text",
        session_name="api-test-session",
        orchestrator_context="evidence context",
        citation_ranks=(1, 3),
    )

    assert answer == "answer text"
    assert calls == [
        [
            "local-ai",
            "chat",
            "question text",
            "--session",
            "api-test-session",
            "--orchestrator-context",
            "evidence context",
            "--citation-ranks",
            "1,3",
        ]
    ]


def test_local_search_results_returns_structured_cached_results(
    monkeypatch,
) -> None:
    from subprocess import CompletedProcess

    from local_ai_search.adapters import local_search

    calls = []

    def run_stub(command, **kwargs):
        calls.append((command, kwargs))
        return CompletedProcess(
            command,
            0,
            stdout='[{"source_type": "web_artifact", "raw_ref": "/tmp/cache.json"}]',
            stderr="",
        )

    monkeypatch.setattr(local_search.subprocess, "run", run_stub)

    results = local_search.search_results(
        "current Python version",
        limit=7,
    )

    assert results == [
        {
            "source_type": "web_artifact",
            "raw_ref": "/tmp/cache.json",
        }
    ]
    assert calls == [
        (
            [
                "local-search",
                "search",
                "current Python version",
                "--limit",
                "7",
                "--json",
                "--local-only",
            ],
            {
                "check": False,
                "capture_output": True,
                "text": True,
            },
        )
    ]


def test_local_search_uses_search_subcommand(monkeypatch) -> None:
    from local_ai_search.adapters import local_search

    calls = []

    monkeypatch.setattr(
        local_search,
        "run_external_command",
        lambda command: calls.append(command) or 0,
    )

    assert local_search.search("Python release") == 0
    assert calls == [
        ["local-search", "search", "Python release"]
    ]