from __future__ import annotations

"""
local_ai/memory.py

Session storage and summarization layer.

Responsibilities:
- Manage session lifecycle (load, save, append, clear)
- Normalize session data across supported shapes (object and legacy list)
- Provide bounded chat history for runtime prompts
- Support manual summarization to keep memory size controlled
- Persist all session data as inspectable JSON files

Design notes:
- Session files are the source of truth (no database, no hidden state)
- Backward compatibility is preserved for older list-based session formats
- Memory is intentionally bounded:
  - recent messages are kept directly
  - older messages may be summarized and replaced
- Summarization is explicit (manual command), not automatic by default
- Logging is used to trace file operations and summarize lifecycle, not content
"""

from datetime import UTC, datetime
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from local_ai.config import CONFIG
from local_ai.log import log_event
from local_ai.paths import paths_get
from local_ai.runtime import ollama_generate, ollama_ensure_running


def timestamp_now_get() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(UTC).isoformat()


def session_path_get(session_name: str | None = None) -> Path:
    """Return the filesystem path for the given session."""
    name = session_name or CONFIG.default_session_name
    sessions_dir = paths_get().sessions_dir
    sessions_dir.mkdir(parents=True, exist_ok=True)
    return sessions_dir / f"{name}.json"


def session_empty_get(session_name: str | None = None) -> dict[str, Any]:
    """Return a new empty session object."""
    name = session_name or CONFIG.default_session_name
    now = timestamp_now_get()

    return {
        "session": name,
        "created_at": now,
        "updated_at": now,
        "summary": None,
        "messages": [],
    }


# WHY:
# Session files may exist in either the current object shape or an older
# list-only shape. Normalize both at load/save boundaries so the rest of the
# module can work against one stable structure without forcing an immediate
# migration step.
def session_normalize(
    data: Any,
    session_name: str | None = None,
) -> dict[str, Any]:
    """Normalize session data into the standard object shape."""
    name = session_name or CONFIG.default_session_name

    if isinstance(data, dict):
        messages = data.get("messages", [])
        if not isinstance(messages, list):
            messages = []

        created_at = data.get("created_at")
        updated_at = data.get("updated_at")
        summary = data.get("summary")

        if created_at is None:
            created_at = _messages_first_timestamp_get(messages)
        if updated_at is None:
            updated_at = _messages_last_timestamp_get(messages)

        return {
            "session": data.get("session", name),
            "created_at": created_at,
            "updated_at": updated_at,
            "summary": summary,
            "messages": messages,
        }

    if isinstance(data, list):
        return {
            "session": name,
            "created_at": _messages_first_timestamp_get(data),
            "updated_at": _messages_last_timestamp_get(data),
            "summary": None,
            "messages": data,
        }

    return session_empty_get(name)


def session_load(session_name: str | None = None) -> dict[str, Any]:
    """Load a session from disk, returning a normalized session object."""
    path = session_path_get(session_name)
    session = session_name or CONFIG.default_session_name

    if not path.exists():
        log_event(
            "session.load.missing",
            session=session,
            path=str(path),
        )
        return session_empty_get(session_name)

    log_event(
        "session.load.start",
        session=session,
        path=str(path),
    )

    with path.open("r", encoding="utf-8") as fh:
        try:
            raw = json.load(fh)
        except JSONDecodeError as exc:
            log_event(
                "session.load.error",
                level="error",
                session=session,
                path=str(path),
                error=f"Malformed JSON: {exc}",
            )
            raise RuntimeError(
                f"Session file '{path}' is malformed JSON. "
                "This likely came from a legacy file shape or interrupted write. "
                "Fix or delete the file."
            ) from exc

    log_event(
        "session.load.ready",
        session=session,
        path=str(path),
    )

    return session_normalize(raw, session_name)


def session_save(
    session_data: dict[str, Any],
    session_name: str | None = None,
) -> None:
    """Persist the given session data to disk."""
    normalized = session_normalize(session_data, session_name)
    session = session_name or CONFIG.default_session_name

    if normalized["created_at"] is None:
        normalized["created_at"] = timestamp_now_get()

    normalized["updated_at"] = timestamp_now_get()

    path = session_path_get(session_name)

    log_event(
        "session.save",
        session=session,
        path=str(path),
    )

    tmp_path = path.with_suffix(".json.tmp")

    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(normalized, fh, indent=2)

    tmp_path.replace(path)


# WHY:
# Only a bounded set of recent conversational turns is passed back into the
# model prompt. This keeps prompt size predictable and avoids feeding back
# non-chat metadata that may exist in the stored session file.
def session_turns_get(session_name: str | None = None) -> list[dict[str, str]]:
    """Return recent conversational turns for prompt construction."""
    session_data = session_load(session_name)
    raw_messages = session_data["messages"]
    turns: list[dict[str, str]] = []

    for item in raw_messages[-CONFIG.memory_turn_limit:]:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant", "system"} and isinstance(content, str):
            turns.append({"role": role, "content": content})

    return turns


def session_append(role: str, content: str, session_name: str | None = None) -> None:
    """Append a new message to the session."""
    session = session_name or CONFIG.default_session_name

    log_event(
        "session.append",
        session=session,
    )

    session_data = session_load(session_name)
    session_data["messages"].append(
        {
            "role": role,
            "content": content,
            "timestamp_utc": timestamp_now_get(),
        }
    )
    session_save(session_data, session_name)


def session_clear(session_name: str | None = None) -> None:
    """Delete the session file if it exists."""
    path = session_path_get(session_name)
    session = session_name or CONFIG.default_session_name

    if path.exists():
        log_event(
            "session.clear",
            session=session,
            path=str(path),
        )
        path.unlink()


def session_names_get() -> list[str]:
    """Return a sorted list of available session names."""
    sessions_dir = paths_get().sessions_dir
    if not sessions_dir.exists():
        return []

    names: list[str] = []
    for path in sessions_dir.glob("*.json"):
        names.append(path.stem)

    return sorted(names)


def session_stats_get(session_name: str) -> dict[str, object]:
    """Return summary statistics for a single session."""
    path = session_path_get(session_name)

    if not path.exists():
        return {"session": session_name, "exists": False}

    try:
        session_data = session_load(session_name)
    except RuntimeError as exc:
        log_event(
            "session.stats.error",
            level="error",
            session=session_name,
            path=str(path),
            error=str(exc),
        )
        return {
            "session": session_name,
            "exists": True,
            "error": "malformed session file",
        }

    messages = session_data["messages"]
    file_size = path.stat().st_size

    total_messages = len(messages)
    total_chars = sum(len(m.get("content", "")) for m in messages)

    user_count = sum(1 for m in messages if m.get("role") == "user")
    assistant_count = sum(1 for m in messages if m.get("role") == "assistant")

    avg_len = total_chars // total_messages if total_messages else 0

    return {
        "session": session_data["session"],
        "exists": True,
        "file_size_bytes": file_size,
        "messages": total_messages,
        "turns_est": min(user_count, assistant_count),
        "user_messages": user_count,
        "assistant_messages": assistant_count,
        "total_chars": total_chars,
        "avg_message_len": avg_len,
        "created_at": session_data["created_at"],
        "last_updated": session_data["updated_at"],
        "has_summary": session_data["summary"] is not None,
    }


def sessions_stats_get() -> list[dict[str, object]]:
    """Return summary statistics for all sessions."""
    summaries: list[dict[str, object]] = []
    for name in session_names_get():
        try:
            summaries.append(session_stats_get(name))
        except Exception as exc:
            log_event(
                "session.stats.aggregate.error",
                level="error",
                session=name,
                error=str(exc),
            )
            summaries.append(
                {
                    "session": name,
                    "exists": True,
                    "error": "failed to process session",
                }
            )
    return summaries


def session_migrate(session_name: str, dry_run: bool = False) -> dict[str, object]:
    """Normalize and rewrite a session into canonical object shape."""
    path = session_path_get(session_name)

    if not path.exists():
        raise RuntimeError(f"Session '{session_name}' does not exist.")

    log_event(
        "session.migrate.start",
        session=session_name,
        path=str(path),
    )

    with path.open("r", encoding="utf-8") as fh:
        try:
            raw = json.load(fh)
        except JSONDecodeError as exc:
            log_event(
                "session.migrate.error",
                level="error",
                session=session_name,
                path=str(path),
                error=f"Malformed JSON: {exc}",
            )
            raise RuntimeError(
                f"Session file '{path}' is malformed JSON. "
                "Migrate only supports valid JSON session files."
            ) from exc

    normalized = session_normalize(raw, session_name)

    changed = raw != normalized

    if dry_run:
        log_event(
            "session.migrate.dry_run",
            session=session_name,
            path=str(path),
        )
        return {
            "session": session_name,
            "path": str(path),
            "changed": changed,
            "written": False,
        }

    session_save(normalized, session_name)

    log_event(
        "session.migrate.ready",
        session=session_name,
        path=str(path),
    )

    return {
        "session": session_name,
        "path": str(path),
        "changed": changed,
        "written": True,
    }


def session_repair(session_name: str, dry_run: bool = False) -> dict[str, object]:
    """Repair one session file conservatively and explicitly."""
    path = session_path_get(session_name)

    if not path.exists():
        raise RuntimeError(f"Session '{session_name}' does not exist.")

    broken_path = path.with_suffix(".json.broken")

    log_event(
        "session.repair.start",
        session=session_name,
        path=str(path),
    )

    try:
        with path.open("r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except JSONDecodeError as exc:
        log_event(
            "session.repair.malformed",
            level="error",
            session=session_name,
            path=str(path),
            error=f"Malformed JSON: {exc}",
        )

        if dry_run:
            return {
                "session": session_name,
                "path": str(path),
                "backup_path": str(broken_path),
                "action": "reset_from_malformed",
                "written": False,
            }

        broken_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        session_save(session_empty_get(session_name), session_name)

        log_event(
            "session.repair.ready",
            session=session_name,
            path=str(path),
            error=None,
        )

        return {
            "session": session_name,
            "path": str(path),
            "backup_path": str(broken_path),
            "action": "reset_from_malformed",
            "written": True,
        }

    normalized = session_normalize(raw, session_name)
    changed = raw != normalized

    if dry_run:
        return {
            "session": session_name,
            "path": str(path),
            "backup_path": None,
            "action": "normalize_valid_json",
            "changed": changed,
            "written": False,
        }

    session_save(normalized, session_name)

    log_event(
        "session.repair.ready",
        session=session_name,
        path=str(path),
        error=None,
    )

    return {
        "session": session_name,
        "path": str(path),
        "backup_path": None,
        "action": "normalize_valid_json",
        "changed": changed,
        "written": True,
    }


def _messages_first_timestamp_get(messages: list[dict[str, Any]]) -> str | None:
    """Return the first available message timestamp."""
    for message in messages:
        timestamp = message.get("timestamp_utc")
        if isinstance(timestamp, str):
            return timestamp
    return None


def _messages_last_timestamp_get(messages: list[dict[str, Any]]) -> str | None:
    """Return the last available message timestamp."""
    for message in reversed(messages):
        timestamp = message.get("timestamp_utc")
        if isinstance(timestamp, str):
            return timestamp
    return None


# WHY:
# Summarization keeps recent raw messages intact while compressing older
# context into a stored summary. This preserves short-term chat continuity
# without letting session files grow without bound. Summarization is explicit
# for now; it does not run automatically in the background.
# SUMMARY POLICY (v4 baseline):
# - Only runs when explicitly invoked (no automatic triggers yet)
# - Keeps last CONFIG.summary_keep_recent_messages raw messages
# - Summarizes up to CONFIG.summary_max_input_messages older messages
# - Caps input to CONFIG.summary_max_input_chars
# - Intended to be bounded, predictable, and inspectable
# NOTE:
# This function performs summarization only when explicitly called.
# Threshold values bound the work performed, but do not trigger automatic runs.
def session_summarize(session_name: str) -> dict[str, object]:
    """Summarize older session messages and persist the result."""
    log_event(
        "session.summarize.start",
        session=session_name,
    )

    session_data = session_load(session_name)
    messages = session_data["messages"]

    if not messages:
        log_event(
            "session.summarize.skip_empty",
            session=session_name,
        )
        return {
            "changed": False,
            "reason": "empty",
        }

    keep_n = CONFIG.summary_keep_recent_messages
    recent_messages = messages[-keep_n:]
    older_messages = messages[:-keep_n]
    max_input = CONFIG.summary_max_input_messages
    older_messages = older_messages[-max_input:]

    if not older_messages:
        log_event(
            "session.summarize.skip_no_older_messages",
            session=session_name,
        )
        return {
            "changed": False,
            "reason": "no_older_messages",
        }

    lines: list[str] = []
    for m in older_messages:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        if isinstance(content, str):
            lines.append(content)

    summary_input = "\n\n".join(lines[-6:])

    max_chars = CONFIG.summary_max_input_chars
    if len(summary_input) > max_chars:
        summary_input = summary_input[-max_chars:]

    ollama_ensure_running()

    prompt = f"Summarize the following text briefly:\n\n{summary_input}"

    try:
        summary_text = ollama_generate(
            prompt,
            model_name=CONFIG.summary_model_name,
        )
        return {
            "changed": True,
            "reason": "summarized",
        }
    except RuntimeError as exc:
        log_event(
            "session.summarize.error",
            level="error",
            session=session_name,
            model=CONFIG.summary_model_name,
            error=str(exc),
        )
        raise RuntimeError(
            f"Session summarize failed for '{session_name}'. "
            "The summarization request may be too large for the current local model/runtime."
        ) from exc

    session_data["summary"] = {
        "text": summary_text,
        "updated_at": timestamp_now_get(),
        "source_message_count": len(messages),
    }

    session_data["messages"] = recent_messages

    session_save(session_data, session_name)

    log_event(
        "session.summarize.ready",
        session=session_name,
        model=CONFIG.summary_model_name,
    )
