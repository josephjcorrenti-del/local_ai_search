from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")

    return subprocess.run(
        [sys.executable, "-m", "local_ai.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def test_read_file_happy_path_with_small_file(tmp_path: Path):
    file_path = tmp_path / "small.txt"
    file_path.write_text("hello file\n", encoding="utf-8")

    result = run_cli("read-file", str(file_path))

    assert result.returncode == 0
    assert f"path: {file_path}" in result.stdout
    assert "size: 11" in result.stdout
    assert "included_chars: 11 of 11" in result.stdout
    assert "hello file" in result.stdout
    assert result.stderr == ""


def test_read_file_truncates_larger_file(tmp_path: Path):
    file_path = tmp_path / "large.txt"
    file_path.write_text("abcdefghij", encoding="utf-8")

    result = run_cli("read-file", str(file_path), "--max-chars", "4")

    assert result.returncode == 0
    assert f"path: {file_path}" in result.stdout
    assert "size: 10" in result.stdout
    assert "included_chars: 4 of 10" in result.stdout
    assert result.stdout.rstrip().endswith("abcd")
    assert "efghij" not in result.stdout
    assert result.stderr == ""


def test_read_file_missing_file_fails(tmp_path: Path):
    file_path = tmp_path / "missing.txt"

    result = run_cli("read-file", str(file_path))

    assert result.returncode != 0
    assert "error:" in result.stderr
    assert f"path does not exist: {file_path}" in result.stderr
    assert "Traceback" not in result.stderr


def test_read_file_directory_fails(tmp_path: Path):
    result = run_cli("read-file", str(tmp_path))

    assert result.returncode != 0
    assert "error:" in result.stderr
    assert f"path is not a file: {tmp_path}" in result.stderr
    assert "Traceback" not in result.stderr

import argparse

from local_ai import cli


def test_file_chat_builds_prompt_from_window(monkeypatch, capsys):
    captured = {}

    def fake_fs_content_window_get(path: str, question: str, max_chars: int):
        captured["path"] = path
        captured["question"] = question
        captured["max_chars"] = max_chars
        return {
            "path": path,
            "size": 100,
            "content_text": "Relevant file content",
            "included_chars": 21,
            "total_chars": 100,
            "truncated": True,
        }

    def fake_ollama_ensure_running():
        captured["ensured"] = True

    def fake_ollama_chat(payload):
        captured["payload"] = payload
        return {"message": {"content": "Fake answer"}}

    monkeypatch.setattr(cli, "fs_content_window_get", fake_fs_content_window_get)
    monkeypatch.setattr(cli, "ollama_ensure_running", fake_ollama_ensure_running)
    monkeypatch.setattr(cli, "ollama_chat", fake_ollama_chat)

    args = argparse.Namespace(
        path="docs/decisions.md",
        question="What is the policy?",
    )

    cli.file_chat_command_run(args)

    assert captured["path"] == "docs/decisions.md"
    assert captured["question"] == "What is the policy?"
    assert captured["ensured"] is True

    payload = captured["payload"]
    assert payload["model"] == cli.CONFIG.chat_model_name
    assert payload["stream"] is False

    user_prompt = payload["messages"][1]["content"]
    assert "Question: What is the policy?" in user_prompt
    assert "File: docs/decisions.md" in user_prompt
    assert "Included chars: 21 of 100" in user_prompt
    assert "Relevant file content" in user_prompt

    output = capsys.readouterr().out
    assert "question: What is the policy?" in output
    assert "path: docs/decisions.md" in output
    assert "included_chars: 21 of 100" in output
    assert "Fake answer" in output
