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
        capture_output=True,
        text=True,
    )


def test_doctor_runs_and_reports_summary() -> None:
    result = run_cli("--verbose", "doctor")

    # In CI, doctor may fail because Ollama/models/scripts are not present.
    # The stable contract is that doctor runs, emits structured logs, and
    # reports failure via command.error when checks fail.
    assert '"message": "command.start"' in result.stdout
    assert '"command": "doctor"' in result.stdout

    if result.returncode == 0:
        assert '"message": "doctor.summary"' in result.stdout
    else:
        assert '"message": "command.error"' in result.stdout
        assert "doctor found" in result.stderr


def test_doctor_accepts_test_data_dir_flag() -> None:
    result = run_cli("--verbose", "--data-dir", "test_data", "doctor")

    # test_data doctor is expected to run against alternate data roots.
    # It may still fail depending on environment/runtime assumptions.
    assert '"message": "command.start"' in result.stdout
    assert '"command": "doctor"' in result.stdout

    if result.returncode == 0:
        assert '"message": "doctor.summary"' in result.stdout
    else:
        assert '"message": "command.error"' in result.stdout
        assert "doctor found" in result.stderr
