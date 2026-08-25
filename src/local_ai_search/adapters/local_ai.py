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


def chat(
    user_prompt: str,
    *,
    session_name: str | None = None,
    orchestrator_context: str | None = None,
    citation_ranks: tuple[int, ...] = (),
) -> str:
    command = ["local-ai", "chat", user_prompt]

    if session_name is not None:
        command.extend(["--session", session_name])

    if orchestrator_context is not None:
        command.extend(
            [
                "--orchestrator-context",
                orchestrator_context,
            ]
        )

    if citation_ranks:
        command.extend(
            [
                "--citation-ranks",
                ",".join(str(rank) for rank in citation_ranks),
            ]
        )

    result = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or "local-ai chat failed"
        )

    return result.stdout.strip()