from __future__ import annotations

from local_ai_search.adapters.subprocesses import run_external_command


def run_status() -> int:
    return run_external_command(["local-search", "status"])


def run_doctor() -> int:
    return run_external_command(["local-search", "doctor"])
