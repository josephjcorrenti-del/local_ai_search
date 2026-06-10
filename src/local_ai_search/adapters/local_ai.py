from __future__ import annotations

import subprocess

from local_ai_search.adapters.subprocesses import run_external_command


def run_status() -> int:
    return run_external_command(["local-ai", "status"])


def run_doctor() -> int:
    return run_external_command(["local-ai", "doctor"])


def ask(prompt: str) -> str:
    result = subprocess.run(
        ["local-ai", "prompt", prompt],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or "local-ai prompt failed"
        )

    return result.stdout.strip()