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


def test_error_without_debug_hides_traceback():
    result = run_cli(
        "repair",
        "--session", "__definitely_missing_session__",
        "--dry-run",
    )

    assert result.returncode != 0

    # Clean user-facing error
    assert "error:" in result.stderr

    # No traceback in normal mode
    assert "Traceback" not in result.stderr


def test_error_with_debug_shows_traceback():
    result = run_cli(
        "--debug",
        "repair",
        "--session", "__definitely_missing_session__",
        "--dry-run",
    )

    assert result.returncode != 0

    # Debug mode shows traceback
    assert "Traceback" in result.stderr

    # Should include exception type
    assert "RuntimeError" in result.stderr
