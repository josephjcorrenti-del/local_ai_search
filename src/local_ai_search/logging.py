from __future__ import annotations

"""
local_ai_search/logging.py

Minimal structured logging helper.

Responsibilities:
- Emit one JSON object per line (NDJSON)
- Always write structured events to run.log
- Emit structured events to stdout only when LOCAL_AI_SEARCH_VERBOSE=1
- Provide a stable, flat event shape for traceability
- Do not use this module for human-facing CLI output
"""

from datetime import UTC, datetime
import inspect
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from local_ai_search.paths import ensure_runtime_dirs


_run_id = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


def log_timestamp_now_get() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_id_get() -> str:
    return _run_id


def elapsed_ms_get(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def _module_name_get(frame_info: inspect.FrameInfo) -> str:
    return Path(frame_info.filename).stem


def _params_build(
    *,
    command: str | None,
    path: str | None,
    error: str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    if command is not None:
        params["command"] = command
    if path is not None:
        params["path"] = path
    if error is not None:
        params["error"] = error

    return params


def log_event(
    event: str,
    *,
    level: str = "INFO",
    command: str | None = None,
    path: str | None = None,
    error: str | None = None,
    event_outcome: str | None = None,
    error_message: str | None = None,
    error_type: str | None = None,
    elapsed_ms: int | None = None,
    result_count: int | None = None,
) -> None:
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

    payload["params"] = _params_build(
        command=command,
        path=path,
        error=error,
    )

    if event_outcome is not None:
        payload["event_outcome"] = event_outcome
    if error_message is not None:
        payload["error_message"] = error_message
    if error_type is not None:
        payload["error_type"] = error_type
    if elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms
    if result_count is not None:
        payload["result_count"] = result_count

    line = json.dumps(payload, ensure_ascii=False)

    if os.environ.get("LOCAL_AI_SEARCH_VERBOSE") == "1":
        print(line)

    paths = ensure_runtime_dirs()

    with paths.run_log.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
