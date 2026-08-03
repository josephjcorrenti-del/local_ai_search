from __future__ import annotations

import subprocess

from local_ai_search.adapters.subprocesses import run_external_command


def run_status() -> int:
    return run_external_command(["local-ai", "status"])


def run_doctor() -> int:
    return run_external_command(["local-ai", "doctor"])


def ask(
    prompt: str,
    *,
    session_name: str | None = None,
    user_content: str | None = None,
) -> str:
    command = ["local-ai", "prompt", prompt]

    if session_name is not None:
        command.extend(["--session", session_name])

    if user_content is not None:
        command.extend(["--user-content", user_content])

    result = subprocess.run(
        command,
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