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


def test_summarize_skips_when_session_is_empty():
    result = run_cli(
        "--data-dir", "test_data",
        "summarize",
        "--session", "empty_messages_session",
    )

    assert result.returncode == 0
    assert "Session skipped" in result.stdout
    assert "reason=empty" in result.stdout


def test_summarize_skips_without_false_summarized_message():
    result = run_cli(
        "--data-dir", "test_data",
        "summarize",
        "--session", "valid_default",
    )

    assert result.returncode == 0
    assert "Session skipped" in result.stdout
    assert "Session summarized" not in result.stdout
