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


def test_migrate_missing_session_fails_cleanly():
    result = run_cli(
        "--data-dir", "test_data",
        "migrate",
        "--session", "__definitely_missing_session__",
        "--dry-run",
    )

    assert result.returncode != 0
    assert "error:" in result.stderr
