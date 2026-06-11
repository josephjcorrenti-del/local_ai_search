from __future__ import annotations

import json
import subprocess
from typing import Any

from local_ai_search.adapters.subprocesses import run_external_command


class LocalSearchAdapterError(Exception):
    pass


def run_status() -> int:
    return run_external_command(["local-search", "status"])


def run_doctor() -> int:
    return run_external_command(["local-search", "doctor"])


def get_evidence(
    path: str,
    *,
    limit: int = 5,
    max_chars: int = 4000,
) -> dict[str, Any]:
    try:
        result = subprocess.run(
            [
                "local-search",
                "evidence",
                path,
                "--limit",
                str(limit),
                "--max-chars",
                str(max_chars),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise LocalSearchAdapterError(
            "local-search command not found; install local_search or activate an environment where local-search is on PATH"
        ) from exc

    if result.returncode != 0:
        raise LocalSearchAdapterError(result.stderr.strip() or "local-search evidence failed")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise LocalSearchAdapterError(f"invalid evidence JSON: {exc}") from exc
