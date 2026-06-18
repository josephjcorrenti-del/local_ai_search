from __future__ import annotations

"""
local_ai/runtime.py

Runtime integration layer for local AI stack (Ollama + helper scripts).

Responsibilities:
- Provide thin wrappers around Ollama HTTP API (GET/POST)
- Ensure Ollama is running before requests (startup + health checks)
- Validate model availability before use
- Execute external helper scripts for AI stack control
- Emit runtime-level logging for traceability (requests, startup, model checks)

Design notes:
- HTTP calls are intentionally simple (urllib, no external client)
- Health checks are performed via /api/version and may be repeated for clarity
- Startup is explicit:
  - if Ollama is not healthy, attempt to start local AI stack
  - retry for a short bounded window before failing
- Model availability is enforced explicitly (no auto-pull)
- Logging captures:
  - request intent (chat/generate)
  - HTTP calls
  - startup and health transitions
  - model validation outcomes
- Prompt/response content is never logged
"""

import json
import subprocess
import time
import urllib.error
import urllib.request
from typing import Any

from local_ai.config import CONFIG
from local_ai.log import log_event
from local_ai.output import info, ok
from local_ai.paths import paths_get


def _elapsed_ms_get(start_ts: float) -> int:
    """Return elapsed time in whole milliseconds."""
    return int((time.perf_counter() - start_ts) * 1000)


def _ollama_get(path: str) -> dict[str, Any]:
    """Perform a GET request to the Ollama API and return parsed JSON."""
    url = f"{CONFIG.ollama_base_url}{path}"
    req = urllib.request.Request(url, method="GET")

    log_event(
        "ollama.http.get",
        path=path,
        url=url,
    )

    started_at = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=CONFIG.request_timeout_s) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        log_event(
            "ollama.http.get.ready",
            path=path,
            url=url,
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        return result

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        elapsed_ms = _elapsed_ms_get(started_at)

        log_event(
            "ollama.http.get.error",
            level="ERROR",
            path=path,
            url=url,
            event_outcome="failure",
            error_message=f"HTTP {exc.code}: {body}",
            error_type=type(exc).__name__,
            error=f"HTTP {exc.code}: {body}",
            elapsed_ms=elapsed_ms,
        )
        raise RuntimeError(f"Ollama HTTP error {exc.code}: {body}") from exc

    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        elapsed_ms = _elapsed_ms_get(started_at)

        log_event(
            "ollama.http.get.error",
            level="ERROR",
            path=path,
            url=url,
            event_outcome="failure",
            error_message=str(reason),
            error_type=type(exc).__name__,
            error=f"Connection failed: {reason}",
            elapsed_ms=elapsed_ms,
        )
        raise RuntimeError(
            f"Failed to connect to Ollama at {CONFIG.ollama_base_url}"
        ) from exc


def _ollama_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Perform a POST request to the Ollama API and return parsed JSON."""
    url = f"{CONFIG.ollama_base_url}{path}"
    model_name = payload.get("model")
    model = model_name if isinstance(model_name, str) else None

    try:
        data = json.dumps(payload).encode("utf-8")
    except (TypeError, ValueError) as exc:
        log_event(
            "ollama.http.post.error",
            level="ERROR",
            path=path,
            url=url,
            model=model,
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            error="Failed to encode POST payload as JSON",
        )
        raise RuntimeError("Failed to encode Ollama request payload as JSON") from exc

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    log_event(
        "ollama.http.post",
        path=path,
        url=url,
        model=model,
    )

    started_at = time.perf_counter()

    try:
        with urllib.request.urlopen(req, timeout=CONFIG.request_timeout_s) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        log_event(
            "ollama.http.post.ready",
            path=path,
            url=url,
            model=model,
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        return result

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        elapsed_ms = _elapsed_ms_get(started_at)

        log_event(
            "ollama.http.post.error",
            level="ERROR",
            path=path,
            url=url,
            model=model,
            event_outcome="failure",
            error_message=f"HTTP {exc.code}: {body}",
            error_type=type(exc).__name__,
            error=f"HTTP {exc.code}: {body}",
            elapsed_ms=elapsed_ms,
        )
        raise RuntimeError(f"Ollama HTTP error {exc.code}: {body}") from exc

    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        elapsed_ms = _elapsed_ms_get(started_at)

        log_event(
            "ollama.http.post.error",
            level="ERROR",
            path=path,
            url=url,
            model=model,
            event_outcome="failure",
            error_message=str(reason),
            error_type=type(exc).__name__,
            error=f"Connection failed: {reason}",
            elapsed_ms=elapsed_ms,
        )
        raise RuntimeError(
            f"Failed to connect to Ollama at {CONFIG.ollama_base_url}"
        ) from exc


def ollama_version_get() -> dict[str, Any]:
    """Return Ollama version information."""
    return _ollama_get("/api/version")


def ollama_models_get() -> list[str]:
    """Return a list of available model names from Ollama."""
    result = _ollama_get("/api/tags")
    models = result.get("models", [])

    if not isinstance(models, list):
        return []

    names: list[str] = []
    for model in models:
        if not isinstance(model, dict):
            continue

        name = model.get("name")
        if isinstance(name, str):
            names.append(name)

    return names


# WHY:
# Health is treated as a simple boolean check: any failure to reach Ollama
# is considered "not healthy". This intentionally hides specific errors at
# this layer so callers can make a simple go/no-go decision.
def ollama_is_healthy() -> bool:
    """Return True if Ollama responds to a basic health check."""
    try:
        ollama_version_get()
        return True
    except Exception:
        return False


def ai_stack_start() -> None:
    """Start the local AI stack using the configured helper script."""
    script_path = paths_get().ai_start_script
    started_at = time.perf_counter()

    log_event(
        "ai.stack.start",
        path=str(script_path),
    )

    try:
        subprocess.run(
            [str(script_path)],
            check=True,
            text=True,
        )
        log_event(
            "ai.stack.ready",
            path=str(script_path),
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
    except subprocess.CalledProcessError as exc:
        log_event(
            "ai.stack.error",
            level="ERROR",
            path=str(script_path),
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            error="AI stack start script failed",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        raise


def ai_status_show() -> None:
    """Display the current status of the local AI stack."""
    script_path = paths_get().ai_status_script
    started_at = time.perf_counter()

    log_event(
        "ai.stack.status",
        path=str(script_path),
    )

    try:
        subprocess.run(
            [str(script_path)],
            check=True,
            text=True,
        )
        log_event(
            "ai.stack.status.ready",
            path=str(script_path),
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
    except subprocess.CalledProcessError as exc:
        log_event(
            "ai.stack.status.error",
            level="ERROR",
            path=str(script_path),
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            error="AI status script failed",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        raise


# WHY:
# Commands assume a working local AI runtime. Instead of failing immediately,
# attempt to start the local stack and retry for a short, bounded window.
# This keeps CLI usage smooth while still failing fast if startup does not succeed.
def ollama_ensure_running() -> None:
    """Ensure Ollama is running, starting it if necessary."""
    started_at = time.perf_counter()

    log_event("ollama.ensure_running.check")

    if ollama_is_healthy():
        log_event(
            "ollama.ensure_running.ready",
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        return

    log_event("ollama.ensure_running.start")
    info("Ollama not healthy. Starting AI stack...")
    ai_stack_start()

    for _ in range(20):
        if ollama_is_healthy():
            log_event(
                "ollama.ensure_running.ready",
                event_outcome="success",
                elapsed_ms=_elapsed_ms_get(started_at),
            )
            ok("Ollama is healthy")
            return
        time.sleep(1)

    log_event(
        "ollama.ensure_running.timeout",
        level="ERROR",
        event_outcome="failure",
        error_message="Ollama did not become healthy after startup",
        error_type="RuntimeError",
        error="Ollama did not become healthy after startup",
        elapsed_ms=_elapsed_ms_get(started_at),
    )
    raise RuntimeError("Ollama did not become healthy after startup")


def ollama_model_ensure_available(model_name: str) -> None:
    """Ensure the given model is available locally, raising if not."""
    started_at = time.perf_counter()

    log_event(
        "ollama.model.ensure_available.check",
        model=model_name,
    )

    available_models = ollama_models_get()

    if model_name in available_models:
        log_event(
            "ollama.model.ensure_available.ready",
            model=model_name,
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        return

    error_text = (
        f"Configured model '{model_name}' is not available in local Ollama. "
        f"Pull it explicitly with: ollama pull {model_name}"
    )

    log_event(
        "ollama.model.ensure_available.missing",
        level="ERROR",
        model=model_name,
        event_outcome="failure",
        error_message=error_text,
        error_type="RuntimeError",
        error=error_text,
        elapsed_ms=_elapsed_ms_get(started_at),
    )

    raise RuntimeError(error_text)


# WHY:
# Chat requests validate model availability before issuing the HTTP call.
# This ensures failures are explicit and local (model missing) rather than
# surfacing later as API errors.
def ollama_chat(payload: dict[str, Any]) -> dict[str, Any]:
    """Send a chat request to Ollama and return the response JSON."""
    started_at = time.perf_counter()

    model_name = payload.get("model")
    model = model_name if isinstance(model_name, str) else None

    log_event(
        "ollama.chat.request",
        model=model,
        path="/api/chat",
    )

    if isinstance(model_name, str):
        ollama_model_ensure_available(model_name)

    result = _ollama_post("/api/chat", payload)

    log_event(
        "ollama.chat.ready",
        model=model,
        path="/api/chat",
        event_outcome="success",
        elapsed_ms=_elapsed_ms_get(started_at),
    )

    return result


# WHY:
# Generate is a simpler prompt-based path that defaults to the configured
# chat model unless explicitly overridden. This keeps summarize and other
# flows flexible without duplicating request logic.
def ollama_generate(prompt: str, model_name: str | None = None) -> str:
    """Generate a completion from Ollama using the given prompt."""
    started_at = time.perf_counter()
    model = model_name or CONFIG.chat_model_name

    log_event(
        "ollama.generate.request",
        model=model,
        path="/api/generate",
    )

    ollama_model_ensure_available(model)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    result = _ollama_post("/api/generate", payload)
    response = result.get("response", "")

    if not isinstance(response, str):
        log_event(
            "ollama.generate.ready",
            model=model,
            path="/api/generate",
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        return ""

    log_event(
        "ollama.generate.ready",
        model=model,
        path="/api/generate",
        event_outcome="success",
        elapsed_ms=_elapsed_ms_get(started_at),
    )

    return response


def ollama_chat_stream(payload: dict[str, Any]):
    """Send a streaming chat request to Ollama and yield content chunks."""
    started_at = time.perf_counter()

    model_name = payload.get("model")
    model = model_name if isinstance(model_name, str) else None

    log_event(
        "ollama.chat.stream.request",
        model=model,
        path="/api/chat",
    )

    if isinstance(model_name, str):
        ollama_model_ensure_available(model_name)

    stream_payload = dict(payload)
    stream_payload["stream"] = True

    url = f"{CONFIG.ollama_base_url}/api/chat"
    data = json.dumps(stream_payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=CONFIG.request_timeout_s) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue

                chunk = json.loads(line)

                message = chunk.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content", "")
                    if isinstance(content, str) and content:
                        yield content

                if chunk.get("done") is True:
                    break

        log_event(
            "ollama.chat.stream.ready",
            model=model,
            path="/api/chat",
            event_outcome="success",
            elapsed_ms=_elapsed_ms_get(started_at),
        )

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        log_event(
            "ollama.chat.stream.error",
            level="ERROR",
            model=model,
            path="/api/chat",
            event_outcome="failure",
            error_message=f"HTTP {exc.code}: {body}",
            error_type=type(exc).__name__,
            error=f"HTTP {exc.code}: {body}",
            elapsed_ms=_elapsed_ms_get(started_at),
        )
        raise RuntimeError(f"Ollama HTTP error {exc.code}: {body}") from exc
