from __future__ import annotations

"""
local_ai/log.py

Minimal structured logging helper.

Responsibilities:
- Emit one JSON object per line (NDJSON)
- Always write structured events to run.log
- Emit structured events to stdout only when OWB_VERBOSE=1
- Provide a stable, flat event shape for traceability
- Do not use this module for human-facing CLI output

Design constraints:
- No hidden configuration or environment-driven behavior
- Keep event structure simple and easy to extend later
- Keep concrete event names stable
- Add normalized optional fields without breaking existing queries
"""

from datetime import UTC, datetime
import inspect
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from local_ai.paths import paths_get

_run_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


def log_timestamp_now_get() -> str:
    """Return current UTC timestamp in log format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id_get() -> str:
    """Return the current process run identifier."""
    return _run_id


def _module_name_get(frame_info: inspect.FrameInfo) -> str:
    """Derive a stable module-style name from the caller filename."""
    return Path(frame_info.filename).stem


def _params_build(
    *,
    command: str | None,
    session: str | None,
    model: str | None,
    path: str | None,
    url: str | None,
    error: str | None,
) -> dict[str, Any]:
    """Build params payload, omitting empty values to reduce noise."""
    params: dict[str, Any] = {}

    if command is not None:
        params["command"] = command
    if session is not None:
        params["session"] = session
    if model is not None:
        params["model"] = model
    if path is not None:
        params["path"] = path
    if url is not None:
        params["url"] = url
    if error is not None:
        params["error"] = error

    return params


def path_display(path: str | Path) -> str:
    value = str(Path(path).expanduser())

    home = str(Path.home())

    if value.startswith(home):
        return value.replace(home, "~", 1)

    return value

def log_event(
    event: str,
    *,
    level: str = "INFO",
    command: str | None = None,
    session: str | None = None,
    model: str | None = None,
    path: str | None = None,
    url: str | None = None,
    error: str | None = None,
    event_outcome: str | None = None,
    error_message: str | None = None,
    error_type: str | None = None,
    elapsed_ms: int | None = None,
) -> None:
    """Emit one structured log event as NDJSON to stdout and run.log."""
    frame_info = inspect.stack()[1]
    fn_name = frame_info.function
    module_name = _module_name_get(frame_info)

    payload: dict[str, Any] = {
        "ts": log_timestamp_now_get(),
        "level": level.upper(),
        "module": module_name,
        "logger": module_name,
        "message": event,
        "run_id": run_id_get(),
        "event": event,
        "fn": fn_name,
    }

    params = _params_build(
        command=command,
        session=session,
        model=model,
        path=path_display(path) if path else None,
        url=url,
        error=error,
    )
    payload["params"] = params

    if event_outcome is not None:
        payload["event_outcome"] = event_outcome

    if error_message is not None:
        payload["error_message"] = error_message

    if error_type is not None:
        payload["error_type"] = error_type

    if elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms

    line = json.dumps(payload, ensure_ascii=False)

    if os.environ.get("OWB_VERBOSE") == "1":
        print(line)

    paths = paths_get()
    paths.logs_dir.mkdir(parents=True, exist_ok=True)

    with paths.run_log_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
