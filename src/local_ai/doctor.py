from __future__ import annotations

"""
local_ai/doctor.py

Doctor checks for local runtime and session health.

Responsibilities:
- Check Ollama reachability
- Check configured model availability
- Check writable session storage
- Check session file validity
- Keep doctor behavior explicit and inspectable

Design notes:
- CLI owns argument parsing and command routing
- doctor.py owns doctor check orchestration
- Output and log behavior should remain unchanged from the CLI implementation
"""

from local_ai.config import CONFIG
from local_ai.log import log_event
from local_ai.memory import session_load, session_names_get
from local_ai.output import fail, ok
from local_ai.paths import paths_get
from local_ai.runtime import (
    ollama_is_healthy,
    ollama_model_ensure_available,
)


def doctor_run() -> None:
    """Run local runtime and session checks."""
    paths = paths_get()
    failures = 0
    checks_run = 0

    # --- Ollama health ---
    if ollama_is_healthy():
        log_event(
            "doctor.check.ok",
            command="doctor",
            event_outcome="success",
        )
        ok("ollama reachable")
        checks_run += 1
    else:
        log_event(
            "doctor.check.fail",
            level="ERROR",
            command="doctor",
            event_outcome="failure",
            error_message="ollama not reachable",
            error_type="RuntimeCheckError",
            error="ollama not reachable",
        )
        fail("ollama not reachable")
        failures += 1

    # --- Model availability ---
    try:
        ollama_model_ensure_available(CONFIG.chat_model_name)
        log_event(
            "doctor.check.ok",
            command="doctor",
            model=CONFIG.chat_model_name,
            event_outcome="success",
        )
        ok(f"chat model available: {CONFIG.chat_model_name}")
        checks_run += 1
    except RuntimeError as exc:
        log_event(
            "doctor.check.fail",
            level="ERROR",
            command="doctor",
            model=CONFIG.chat_model_name,
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            error=f"chat model lookup failed: {CONFIG.chat_model_name}",
        )
        fail(f"chat model lookup failed: {CONFIG.chat_model_name}")
        failures += 1

    # --- Sessions dir writable ---
    try:
        paths.sessions_dir.mkdir(parents=True, exist_ok=True)
        test_path = paths.sessions_dir / ".doctor_write_test"
        test_path.write_text("ok\n", encoding="utf-8")
        test_path.unlink()

        log_event(
            "doctor.check.ok",
            command="doctor",
            path=str(paths.sessions_dir),
            event_outcome="success",
        )
        ok(f"sessions dir writable: {paths.sessions_dir}")
        checks_run += 1
    except OSError as exc:
        log_event(
            "doctor.check.fail",
            level="ERROR",
            command="doctor",
            path=str(paths.sessions_dir),
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        fail(f"sessions dir not writable: {paths.sessions_dir}")
        failures += 1

    # --- Session validity ---
    for session_name in session_names_get():
        checks_run += 1
        try:
            session_load(session_name)
            log_event(
                "doctor.check.ok",
                command="doctor",
                session=session_name,
                event_outcome="success",
            )
            ok(f"session valid: {session_name}")
        except RuntimeError as exc:
            log_event(
                "doctor.check.fail",
                level="ERROR",
                command="doctor",
                session=session_name,
                event_outcome="failure",
                error_message=str(exc),
                error_type=type(exc).__name__,
                error=str(exc),
            )
            fail(f"session invalid: {session_name}")
            failures += 1

    # --- Summary ---
    log_event(
        "doctor.summary",
        command="doctor",
        error=None if failures == 0 else f"{failures} failing check(s)",
    )

    if failures:
        fail(f"doctor run failed: {failures} failing check(s)")
        raise RuntimeError(f"doctor found {failures} failing check(s)")

    ok(f"doctor passed ({checks_run} checks)")
