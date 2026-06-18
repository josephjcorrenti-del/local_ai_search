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


def test_status_runs_and_prints_core_sections():
    result = run_cli("status")

    assert result.returncode == 0
    assert "app: local_ai" in result.stdout
    assert "runtime:" in result.stdout
    assert "paths:" in result.stdout
    assert "app_data_root:" in result.stdout
    assert "sessions_dir:" in result.stdout
    assert "system:" in result.stdout


def test_status_accepts_test_data_dir_flag():
    result = run_cli("--data-dir", "test_data", "status")

    assert result.returncode == 0
    assert "app: local_ai" in result.stdout
    assert "paths:" in result.stdout
    assert "app_data_root:" in result.stdout
    assert "sessions_dir:" in result.stdout
