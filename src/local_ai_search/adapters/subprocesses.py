from __future__ import annotations

import subprocess


def run_external_command(command: list[str]) -> int:
    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError:
        return 127

    return result.returncode
