from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_cli(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    return subprocess.run(
        [
            sys.executable,
            "-m",
            "local_ai.cli",
            "--data-dir",
            str(tmp_path),
            *args,
        ],
        cwd=Path(__file__).resolve().parents[3],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_profile_cli_lifecycle(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "profile-show")
    assert result.returncode == 0

    profile = json.loads(result.stdout)
    assert profile == {
        "profile_key": "default",
        "enabled": False,
        "values": {},
    }

    result = run_cli(tmp_path, "profile-enable")
    assert result.returncode == 0
    assert "Profile enabled (default)" in result.stdout

    result = run_cli(tmp_path, "profile-set", "display name", "Joe")
    assert result.returncode == 0
    assert "Profile value set" in result.stdout

    result = run_cli(tmp_path, "profile-set", "preferred model", "phi3:mini")
    assert result.returncode == 0
    assert "Profile value set" in result.stdout

    result = run_cli(tmp_path, "profile-show")
    assert result.returncode == 0

    profile = json.loads(result.stdout)
    assert profile["enabled"] is True
    assert profile["values"]["display_name"] == "Joe"
    assert profile["values"]["preferred_model"] == "phi3:mini"

    result = run_cli(tmp_path, "profile-clear", "preferred model")
    assert result.returncode == 0

    result = run_cli(tmp_path, "profile-disable")
    assert result.returncode == 0
    assert "Profile disabled (default)" in result.stdout

    result = run_cli(tmp_path, "profile-show")
    assert result.returncode == 0

    profile = json.loads(result.stdout)
    assert profile["enabled"] is False
    assert profile["values"] == {
        "display_name": "Joe",
    }

    result = run_cli(tmp_path, "profile-delete")
    assert result.returncode == 0
    assert "Profile deleted" in result.stdout

    result = run_cli(tmp_path, "profile-show")
    assert result.returncode == 0

    profile = json.loads(result.stdout)
    assert profile == {
        "profile_key": "default",
        "enabled": False,
        "values": {},
    }


def test_profile_cli_delete_absent_profile(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "profile-delete")

    assert result.returncode == 0
    assert "Profile already absent" in result.stdout
