from __future__ import annotations

import argparse
import readline
import shlex
import time
from typing import Callable

from local_ai.config import CONFIG
from local_ai.log import log_event
from local_ai.output import fail, info, ok
from local_ai.profile import profile_load
from local_ai.runtime import ollama_chat, ollama_ensure_running
from local_ai.workspace import (
    workspace_create,
    workspace_load,
    workspace_session_add,
)

SHELL_HELP = """
Available commands:

Core:
  chat <message>
  status
  doctor

File:
  read-file <path> [--max-chars N]
  file-chat <path> <question>

Web:
  web-fetch <url>
  web-search <query> [--limit N]
  web-chat <question> --url <url>
  web-chat <question> --query <query> [--limit N]

Session:
  session
  session NAME
  sessions
  stats [--session NAME]
  summarize [--session NAME] [--all]
  clear [--session NAME]

Maintenance:
  repair --session NAME [--dry-run]
  migrate [--session NAME] [--all] [--dry-run]
  web-cleanup [--days N] [--delete]

Shell:
  help
  banner
  session
  session NAME
  exit
  quit

Profile:
  profile-show
  profile-enable [--profile KEY]
  profile-disable [--profile KEY]
  profile-set <human-readable-key> <value> [--profile KEY]
  profile-clear <human-readable-key> [--profile KEY]
  profile-delete

Default:
  Any input that does not start with a known command is treated as:
    chat <input> using the active shell session

Examples:

  hello world
    chat using the active shell session

  chat "hello" --session scratch
    chat using an explicit session override

  session project-notes
    switch the active shell session

  banner
    show current shell model and active session

  file-chat README.md "what does this project do?"
    ask about one explicit local file

  web-chat "summarize this page" --url https://example.com
    ask about one explicit URL

  web-chat "python logging basics" --query "python logging best practices"
    search the web and answer from fetched sources

Workspace:
  workspace
  workspace NAME
  workspace-create <name>
  workspace-list
  workspace-show <name>
  workspace-add-session <workspace> <session>
  workspace-add-file <workspace> <path>
  workspace-add-web-artifact <workspace> <artifact_path>
  workspace-chat <workspace> <question>

  local-ai shell
    starts shell; auto-loads enabled default profile if present

  local-ai shell --profile joe
    starts shell with named enabled profile
""".strip()


def shell_line_run(
    line: str,
    state: dict[str, str],
    *,
    parser_build: Callable[[], argparse.ArgumentParser],
    command_handlers: dict[str, Callable[[argparse.Namespace], None]],
    chat_run: Callable[..., None],
) -> None:
    """Run one shell input line through the existing CLI parser/handlers."""

    stripped = line.strip()
    if not stripped:
        return

    if stripped == "banner":
        print("local-ai shell")
        print(f"profile: {state.get('profile') or '(none)'}")
        print(f"model: {state['model']}")
        print(f"workspace: {state.get('workspace') or '(none)'}")
        print(f"session: {state['session']}")
        return

    if stripped == "session":
        print(f"session: {state['session']}")
        return

    if stripped.startswith("session "):
        state["session"] = stripped.split(" ", 1)[1].strip()
        ok(f"Session set ({state['session']})")
        _workspace_session_link_if_active(state)
        return

    if stripped.startswith("workspace "):
        name = stripped.split(" ", 1)[1].strip()

        # lazy create or validate
        try:
            workspace_load(name)
        except Exception:
            workspace_create(name)

        state["workspace"] = name
        ok(f"Workspace set ({name})")
        _workspace_session_link_if_active(state)
        return

    if stripped == "workspace":
        if state.get("workspace"):
            print(f"workspace: {state['workspace']}")
        else:
            print("workspace: (none)")
        return

    if stripped in {"help", "?"}:
        print(SHELL_HELP)
        return

    if stripped in {"exit", "quit"}:
        raise EOFError

    try:
        parts = shlex.split(stripped)
    except ValueError as exc:
        fail(f"parse error: {exc}")
        return

    if not parts:
        return

    known_commands = set(command_handlers)

    if parts[0] in known_commands:
        argv = parts
    else:
        argv = ["chat", stripped]

    if argv[0] == "chat" and "--session" not in argv:
        argv.extend(["--session", state["session"]])

    parser = parser_build()
    args = parser.parse_args(argv)

    command = args.command
    handler = command_handlers.get(command)

    if handler is None:
        raise RuntimeError(f"Unknown command: {command}")

    started_at = time.perf_counter()

    log_event(
        "command.start",
        command=command,
    )

    try:
        if command == "chat":
            chat_run(args.text, args.session, state["model"], stream=True)
        else:
            handler(args)
    except Exception as exc:
        log_event(
            "command.error",
            level="ERROR",
            command=command,
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            error=str(exc),
            elapsed_ms=int((time.perf_counter() - started_at) * 1000),
        )
        fail(f"error: {exc}")
        return

    log_event(
        "command.end",
        command=command,
        event_outcome="success",
        elapsed_ms=int((time.perf_counter() - started_at) * 1000),
    )


def shell_command_run(
    args: argparse.Namespace,
    *,
    parser_build: Callable[[], argparse.ArgumentParser],
    command_handlers: dict[str, Callable[[argparse.Namespace], None]],
    chat_run: Callable[..., None],
) -> None:
    profile = _profile_for_shell_get(args.profile)

    profile_values = profile.get("values", {}) if profile else {}

    model_name = CONFIG.small_model_name if args.small else CONFIG.chat_model_name

    if not args.small and profile_values.get("preferred_model"):
        model_name = str(profile_values["preferred_model"])

    state = {
        "session": str(profile_values.get("preferred_session") or CONFIG.default_session_name),
        "model": model_name,
        "workspace": profile_values.get("preferred_workspace"),
        "profile": profile["profile_key"] if profile else None,
    }

    print("local-ai shell")
    if state.get("profile"):
        print(f"profile: {state['profile']}")
    print(f"model: {state['model']}")
    print(f"workspace: {state.get('workspace') or '(none)'}")
    print(f"session: {state['session']}")
    info("Warming model...")
    shell_warmup_run(state["model"])
    info("Model ready")
    print("type help for commands, exit to quit")
    print()

    while True:
        try:
            line = input(_prompt_get(state))
            shell_line_run(
                line,
                state,
                parser_build=parser_build,
                command_handlers=command_handlers,
                chat_run=chat_run,
            )
        except EOFError:
            print()
            info("Exiting shell")
            break
        except KeyboardInterrupt:
            print()
            continue


def shell_warmup_run(model_name: str) -> None:
    """Warm LLM up, Kris.  I'm about to."""
    ollama_ensure_running()

    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly: ready",
            }
        ],
    }

    ollama_chat(payload)


def _workspace_session_link_if_active(state: dict[str, str]) -> None:
    workspace_name = state.get("workspace")
    session_name = state.get("session")

    if workspace_name and session_name:
        workspace_session_add(workspace_name, session_name)


def _prompt_get(state: dict[str, str]) -> str:
    workspace_name = state.get("workspace")
    session_name = state["session"]

    if workspace_name:
        return f"local-ai:{workspace_name}.{session_name}> "

    return f"local-ai:{session_name}> "


def _profile_for_shell_get(profile_key: str | None) -> dict[str, object] | None:
    """Load an enabled profile for shell startup, if available."""
    profile = profile_load(profile_key)

    if not profile.get("enabled"):
        return None

    return profile
