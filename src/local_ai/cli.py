from __future__ import annotations

"""
local_ai/cli.py

Primary CLI entrypoint and command router.

Responsibilities:
- Define CLI commands and argument parsing (argparse)
- Route commands to small handler functions
- Keep handlers thin and explicit (no hidden behavior)
- Coordinate between runtime, memory, tools, and web modules
- Emit command-level logging (start / end / error)

Design notes:
- CLI is intentionally "flat": each command maps to one handler
- Business logic lives in other modules (runtime, memory, web)
- Output is intentionally separated:
  - Human-readable command output uses print() or output.py helpers
  - Machine-readable structured logs use log_event()
  - --verbose controls whether structured logs are also shown in terminal
- No background behavior: all actions are explicit per command
"""

import argparse
import json
import os
import sys
import time
from typing import Callable

from local_ai.config import CONFIG
from local_ai.doctor import doctor_run
from local_ai.fs import fs_content_window_get, fs_read
from local_ai.log import log_event
from local_ai.memory import (
    session_append,
    session_clear,
    session_migrate,
    session_names_get,
    session_repair,
    session_stats_get,
    session_summarize,
    session_turns_get,
    sessions_stats_get,
)
from local_ai.output import fail, info, ok, warn
from local_ai.paths import paths_get
from local_ai.profile import (
    profile_clear,
    profile_delete,
    profile_disable,
    profile_enable,
    profile_load,
    profile_set,
)
from local_ai.runtime import (
    ai_status_show,
    ollama_chat,
    ollama_chat_stream,
    ollama_ensure_running,
    ollama_is_healthy,
)
from local_ai.schemas import PING_SCHEMA
from local_ai.shell import shell_command_run as shell_run
from local_ai.tools import TOOL_DEFS, TOOL_REGISTRY
from local_ai.web import (
    web_artifact_content_window_get,
    web_cleanup,
    web_fetch,
    web_search,
)
from local_ai.workspace import (
    workspace_create,
    workspace_file_add,
    workspace_load,
    workspace_names_get,
    workspace_session_add,
    workspace_web_artifact_add,
)


def prompt_run(user_prompt: str) -> None:
    """Run a one-off prompt against the local model."""
    ollama_ensure_running()

    payload = {
        "model": CONFIG.chat_model_name,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a concise local assistant. "
                    "Answer clearly and directly."
                ),
            },
            {"role": "user", "content": user_prompt},
        ],
    }

    result = ollama_chat(payload)
    print(result["message"]["content"])


def json_run() -> None:
    """Run a structured JSON response test using the local model."""
    ollama_ensure_running()

    payload = {
        "model": CONFIG.chat_model_name,
        "stream": False,
        "format": PING_SCHEMA,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return valid JSON only. "
                    "Do not include markdown fences."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return a short health summary for this local stack. "
                    "Set status=ok, model to the active model name, "
                    "and summary to one sentence."
                ),
            },
        ],
    }

    result = ollama_chat(payload)
    content = result["message"]["content"]
    parsed = json.loads(content)
    print(json.dumps(parsed, indent=2))


# WHY:
# Tool-calling is kept as an explicit demo/test flow. The CLI shows the tool
# request, executes the selected local tool, and feeds the result back to the
# model so the full interaction stays visible and inspectable.
def tool_run(path: str) -> None:
    """Demonstrate tool-calling by listing and summarizing a directory."""
    ollama_ensure_running()

    messages = [
        {
            "role": "system",
            "content": (
                "You may use tools when helpful. "
                "If the user asks about local files, call the directory_list tool. "
                "Do not describe the tool call in prose. "
                "Prefer returning an actual tool call."
            ),
        },
        {
            "role": "user",
            "content": f"List the contents of this directory and summarize it: {path}",
        },
    ]

    first = ollama_chat(
        {
            "model": CONFIG.chat_model_name,
            "stream": False,
            "messages": messages,
            "tools": TOOL_DEFS,
        }
    )

    assistant_message = first["message"]
    messages.append(assistant_message)

    tool_calls = assistant_message.get("tool_calls", [])

    if not tool_calls:
        content = assistant_message.get("content", "").strip()

        try:
            parsed_tool = json.loads(content)
        except json.JSONDecodeError:
            parsed_tool = None

        if (
            isinstance(parsed_tool, dict)
            and "name" in parsed_tool
            and "arguments" in parsed_tool
            and isinstance(parsed_tool["arguments"], dict)
        ):
            tool_calls = [
                {
                    "function": {
                        "name": parsed_tool["name"],
                        "arguments": parsed_tool["arguments"],
                    }
                }
            ]
        else:
            warn("Model did not call a tool")
            print(content)
            return

    for tool_call in tool_calls:
        fn = tool_call["function"]["name"]
        args = tool_call["function"]["arguments"]

        info(f"Executing tool: {fn}({args})")

        tool_fn = TOOL_REGISTRY[fn]
        tool_result = tool_fn(**args)

        info("Tool result:")
        print(json.dumps(tool_result, indent=2))

        messages.append(
            {
                "role": "tool",
                "name": fn,
                "content": json.dumps(tool_result),
            }
        )

    messages.append(
        {
            "role": "system",
            "content": (
                "You have already received the tool result. "
                "Do not call any more tools. "
                "Summarize the directory contents for the user."
            ),
        }
    )

    final = ollama_chat(
        {
            "model": CONFIG.chat_model_name,
            "stream": False,
            "messages": messages,
        }
    )

    print()
    info("Final answer:")
    print(final["message"]["content"])


def chat_run(
    user_prompt: str,
    session_name: str | None = None,
    model_name: str | None = None,
    stream: bool = False,
) -> None:
    """Run chat with optional session memory persistence."""
    ollama_ensure_running()

    model = model_name or CONFIG.chat_model_name

    messages = [
        {
            "role": "system",
            "content": (
                "You are a concise local assistant. "
                "Help with general questions, coding, debugging, and technical reasoning. "
                "Be practical and direct."
            ),
        }
    ]

    messages.extend(session_turns_get(session_name))
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": model,
        "stream": stream,
        "messages": messages,
    }

    if stream:
        parts: list[str] = []
        for chunk in ollama_chat_stream(payload):
            print(chunk, end="", flush=True)
            parts.append(chunk)
        print()
        answer = "".join(parts)
    else:
        result = ollama_chat(payload)
        answer = result["message"]["content"]
        print(answer)

    session_append("user", user_prompt, session_name)
    session_append("assistant", answer, session_name)

def clear_run(session_name: str | None = None) -> None:
    """Clear stored messages for a session."""
    session_clear(session_name)
    ok("Session cleared")


def prompt_command_run(args: argparse.Namespace) -> None:
    prompt_run(args.text)


def json_command_run(args: argparse.Namespace) -> None:
    json_run()


def tool_command_run(args: argparse.Namespace) -> None:
    tool_run(args.path)


def chat_command_run(args: argparse.Namespace) -> None:
    chat_run(args.text, args.session)


def clear_command_run(args: argparse.Namespace) -> None:
    clear_run(args.session)


def sessions_command_run(args: argparse.Namespace) -> None:
    del args
    for name in session_names_get():
        print(name)


def stats_command_run(args: argparse.Namespace) -> None:
    if args.session:
        print(json.dumps(session_stats_get(args.session), indent=2))
        return

    print(json.dumps(sessions_stats_get(), indent=2))


# WHY:
# Summarization is always operator-invoked from the CLI.
# Even batch summarization via --all is explicit and does not imply
# background or automatic summarization policy.
def summarize_command_run(args: argparse.Namespace) -> None:
    """Run explicit session summarization for one session or all sessions."""
    if args.all:
        for name in session_names_get():
            result = session_summarize(name)
            if result["changed"]:
                ok(f"Session summarized ({name})")
            else:
                info(f"Session skipped ({name}) reason={result['reason']}")
        return

    session_name = args.session or CONFIG.default_session_name
    result = session_summarize(session_name)

    if result["changed"]:
        ok(f"Session summarized ({session_name})")
    else:
        info(f"Session skipped ({session_name}) reason={result['reason']}")


def status_command_run(args: argparse.Namespace) -> None:
    """Display runtime configuration and system status."""
    del args

    paths = paths_get()

    print(f"app: {CONFIG.app_name}")
    print()

    print("runtime:")
    print(f"  ollama_base_url: {CONFIG.ollama_base_url}")
    print(f"  ollama_healthy: {'yes' if ollama_is_healthy() else 'no'}")
    print(f"  chat_model: {CONFIG.chat_model_name}")
    print(f"  summary_model: {CONFIG.summary_model_name}")
    print()

    print("paths:")
    print(f"  repo_root: {paths.repo_root}")
    print(f"  app_data_root: {paths.app_data_root}")
    print(f"  sessions_dir: {paths.sessions_dir}")
    print()

    print("system:")
    ai_status_show()


def web_fetch_command_run(args: argparse.Namespace) -> None:
    """Fetch a URL and display a preview of the stored artifact."""
    artifact = web_fetch(args.url)

    print(f"url: {artifact['url']}")
    print(f"fetched_at: {artifact['fetched_at']}")
    print(f"title: {artifact.get('title') or '(none)'}")
    print(f"artifact_path: {artifact['artifact_path']}")
    print()

    content_text = artifact.get("content_text", "")
    preview = content_text[:500]
    if len(content_text) > 500:
        preview += "..."

    print(preview)


def web_search_command_run(args: argparse.Namespace) -> None:
    """Search the web and print fetched artifact summaries."""
    results = web_search(args.query, args.limit)

    print(f"query: {args.query}")
    print(f"results: {len(results)}")
    print()

    for i, artifact in enumerate(results, 1):
        print(f"[{i}]")
        print(f"title: {artifact.get('title') or '(none)'}")
        print(f"url: {artifact['url']}")
        print(f"artifact_path: {artifact['artifact_path']}")
        print()


def web_chat_command_run(args: argparse.Namespace) -> None:
    """Answer a question using one explicit URL or a search query."""
    if args.url:
        artifact = web_fetch(args.url)
        artifacts = [artifact]
    elif args.query:
        artifacts = web_search(args.query, args.limit)
        if not artifacts:
            raise RuntimeError(f"No web results found for query: {args.query}")
    else:
        raise RuntimeError("web-chat requires either --url or --query")

    source_windows = []
    for artifact in artifacts:
        content_window = web_artifact_content_window_get(
            artifact,
            CONFIG.web_chat_max_source_chars,
            question=args.question,
        )

    combined_parts: list[str] = []
    for i, (artifact, content_window) in enumerate(source_windows, 1):
        combined_parts.append(
            f"[Source {i}]\n"
            f"URL: {artifact['url']}\n"
            f"Title: {artifact.get('title') or '(none)'}\n"
            f"Included chars: {content_window['included_chars']} "
            f"of {content_window['total_chars']}\n\n"
            f"Page content:\n{content_window['content_text']}"
        )

    prompt = (
        f"Question: {args.question}\n\n"
        f"{chr(10).join(combined_parts)}"
    )

    ollama_ensure_running()

    payload = {
        "model": CONFIG.chat_model_name,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using only the provided web page content. "
                    "Be concise and say when the provided pages do not contain enough information."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    result = ollama_chat(payload)
    answer = result["message"]["content"]

    print(f"question: {args.question}")
    if args.url:
        print("mode: single-url")
    else:
        print(f"mode: query-search ({len(artifacts)} source(s))")
    print()

    for i, (artifact, content_window) in enumerate(source_windows, 1):
        print(f"[{i}]")
        print(f"url: {artifact['url']}")
        print(f"artifact_path: {artifact['artifact_path']}")
        print(
            f"included_chars: {content_window['included_chars']} "
            f"of {content_window['total_chars']}"
        )
        print()

    print(answer)


def web_cleanup_command_run(args: argparse.Namespace) -> None:
    """List or delete old web artifacts."""
    removed = web_cleanup(args.days, args.delete)

    if not removed:
        info("No old web artifacts found.")
        return

    if args.delete:
        ok(f"Deleted {len(removed)} artifact(s):")
    else:
        info(f"Would delete {len(removed)} artifact(s):")

    for path in removed:
        print(f"  {path}")


def doctor_command_run(args: argparse.Namespace) -> None:
    """Run local runtime checks."""
    del args
    doctor_run()


def migrate_command_run(args: argparse.Namespace) -> None:
    """Normalize and rewrite one session or all sessions."""
    if args.all:
        names = session_names_get()
        if not names:
            info("No sessions found.")
            return

        for name in names:
            result = session_migrate(name, dry_run=args.dry_run)
            if args.dry_run:
                info(f"Would migrate ({name}) changed={result['changed']}")
            else:
                ok(f"Session migrated ({name}) changed={result['changed']}")
        return

    session_name = args.session or CONFIG.default_session_name
    result = session_migrate(session_name, dry_run=args.dry_run)

    if args.dry_run:
        info(f"Would migrate ({session_name}) changed={result['changed']}")
    else:
        ok(f"Session migrated ({session_name}) changed={result['changed']}")


def repair_command_run(args: argparse.Namespace) -> None:
    """Repair one session file conservatively and explicitly."""
    if not args.session:
        raise RuntimeError("repair requires --session")

    result = session_repair(args.session, dry_run=args.dry_run)

    if args.dry_run:
        if result["action"] == "reset_from_malformed":
            info(
                f"Would repair ({args.session}) by backing up malformed file "
                f"to {result['backup_path']} and resetting the session"
            )
        else:
            info(
                f"Would repair ({args.session}) by normalizing valid JSON "
                f"changed={result['changed']}"
            )
        return

    if result["action"] == "reset_from_malformed":
        ok(
            f"Session repaired ({args.session}); malformed file backed up to "
            f"{result['backup_path']} and session reset"
        )
    else:
        ok(
            f"Session repaired ({args.session}); normalized valid JSON "
            f"changed={result['changed']}"
        )


def read_file_command_run(args: argparse.Namespace) -> None:
    """Read one explicit local file and print bounded content."""
    result = fs_read(args.path, args.max_chars)

    print(f"path: {result['path']}")
    print(f"size: {result['size']}")
    print(
        f"included_chars: {result['included_chars']} "
        f"of {result['size']}"
    )
    print()
    print(result["content"])


def file_chat_command_run(args: argparse.Namespace) -> None:
    """Answer a question using one explicit local file."""
    content_window = fs_content_window_get(
        args.path,
        args.question,
        CONFIG.web_chat_max_source_chars,
    )

    prompt = (
        f"Question: {args.question}\n\n"
        f"File: {content_window['path']}\n"
        f"Included chars: {content_window['included_chars']} "
        f"of {content_window['total_chars']}\n\n"
        f"File content:\n{content_window['content_text']}"
    )

    ollama_ensure_running()

    payload = {
        "model": CONFIG.chat_model_name,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer the user's question using only the provided file content. "
                    "Be concise and say when the provided file content does not contain enough information."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    result = ollama_chat(payload)
    answer = result["message"]["content"]

    print(f"question: {args.question}")
    print(f"path: {content_window['path']}")
    print(
        f"included_chars: {content_window['included_chars']} "
        f"of {content_window['total_chars']}"
    )
    print()
    print(answer)


def shell_command_run(args: argparse.Namespace) -> None:
    """Run an interactive local-ai shell."""
    shell_run(
        args,
        parser_build=parser_build,
        command_handlers=COMMAND_HANDLERS,
        chat_run=chat_run,
    )


def workspace_create_command_run(args: argparse.Namespace) -> None:
    workspace_create(args.name)
    ok(f"Workspace created ({args.name})")


def workspace_list_command_run(args: argparse.Namespace) -> None:
    del args
    for name in workspace_names_get():
        print(name)


def workspace_show_command_run(args: argparse.Namespace) -> None:
    data = workspace_load(args.name)
    print(json.dumps(data, indent=2))


def workspace_add_session_command_run(args: argparse.Namespace) -> None:
    result = workspace_session_add(args.workspace, args.session)

    if result["changed"]:
        ok(f"Workspace session added ({args.workspace}) session={args.session}")
    else:
        info(f"Workspace session already linked ({args.workspace}) session={args.session}")


def workspace_add_file_command_run(args: argparse.Namespace) -> None:
    result = workspace_file_add(args.workspace, args.path)

    if result["changed"]:
        ok(f"Workspace file added ({args.workspace}) path={args.path}")
    else:
        info(f"Workspace file already linked ({args.workspace}) path={args.path}")


def workspace_add_web_artifact_command_run(args: argparse.Namespace) -> None:
    result = workspace_web_artifact_add(args.workspace, args.artifact_path)

    if result["changed"]:
        ok(
            f"Workspace web artifact added ({args.workspace}) "
            f"path={args.artifact_path}"
        )
    else:
        info(
            f"Workspace web artifact already linked ({args.workspace}) "
            f"path={args.artifact_path}"
        )


def workspace_chat_command_run(args: argparse.Namespace) -> None:
    workspace = workspace_load(args.workspace)

    session_names = workspace.get("sessions", [])
    file_paths = workspace.get("files", [])
    web_artifact_paths = workspace.get("web_artifacts", [])

    source_parts = []
    source_report = []

    for session_name in session_names:
        turns = session_turns_get(session_name)
        included_turns = turns[-8:]
        text = "\n".join(
            f"{turn.get('role')}: {turn.get('content')}"
            for turn in included_turns
        )

        source_parts.append(
            f"[Session: {session_name}]\n{text}"
        )
        source_report.append(
            f"session: {session_name} turns_included={len(included_turns)}"
        )

    for path in file_paths:
        window = fs_content_window_get(
            path,
            args.question,
            CONFIG.web_chat_max_source_chars,
        )

        source_parts.append(
            f"[File: {window['path']}]\n"
            f"Included chars: {window['included_chars']} "
            f"of {window['total_chars']}\n\n"
            f"{window['content_text']}"
        )
        source_report.append(
            f"file: {window['path']} "
            f"included_chars={window['included_chars']} "
            f"of {window['total_chars']}"
        )

    for artifact_path in web_artifact_paths:
        with open(artifact_path, "r", encoding="utf-8") as f:
            artifact = json.load(f)

        window = web_artifact_content_window_get(
            artifact,
            CONFIG.web_chat_max_source_chars,
            question=args.question,
        )

        source_parts.append(
            f"[Web artifact: {artifact_path}]\n"
            f"URL: {artifact.get('url')}\n"
            f"Title: {artifact.get('title') or '(none)'}\n"
            f"Included chars: {window['included_chars']} "
            f"of {window['total_chars']}\n\n"
            f"{window['content_text']}"
        )
        source_report.append(
            f"web_artifact: {artifact_path} "
            f"included_chars={window['included_chars']} "
            f"of {window['total_chars']}"
        )

    prompt = (
        f"Workspace: {args.workspace}\n"
        f"Question: {args.question}\n\n"
        f"Sources:\n\n"
        f"{chr(10).join(source_parts)}"
    )

    ollama_ensure_running()

    payload = {
        "model": CONFIG.chat_model_name,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Answer using only the provided workspace sources. "
                    "If the sources do not contain enough information, say so."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    result = ollama_chat(payload)
    answer = result["message"]["content"]

    print(f"workspace: {args.workspace}")
    print(f"question: {args.question}")
    print()
    print("sources:")
    for source in source_report:
        print(f"  {source}")
    print()
    print("answer:")
    print(answer)


def profile_show_command_run(args: argparse.Namespace) -> None:
    profile = profile_load(args.profile)
    print(json.dumps(profile, indent=2))


def profile_enable_command_run(args: argparse.Namespace) -> None:
    profile = profile_enable(args.profile)


    ok(f"Profile enabled ({profile['profile_key']})")
def profile_disable_command_run(args: argparse.Namespace) -> None:
    profile = profile_disable(args.profile)


    ok(f"Profile disabled ({profile['profile_key']})")
def profile_delete_command_run(args: argparse.Namespace) -> None:
    deleted = profile_delete()


    if deleted:
        ok("Profile deleted")
    else:
        info("Profile already absent")


def profile_set_command_run(args: argparse.Namespace) -> None:
    profile = profile_set(
        args.key,
        args.value,
        profile_key=args.profile,
    )


    ok(
        f"Profile value set "
        f"({profile['profile_key']}) "
        f"{args.key}={args.value}"
    )


def profile_clear_command_run(args: argparse.Namespace) -> None:
    profile = profile_clear(
        args.key,
        profile_key=args.profile,
    )


    ok(
        f"Profile value cleared "
        f"({profile['profile_key']}) "
        f"{args.key}"
    )


def argv_normalize(argv: list[str]) -> list[str]:
    if not argv:
        return argv

    first = argv[0]

    if first.startswith("-"):
        return argv

    if first in COMMAND_HANDLERS:
        return argv

    return ["chat", " ".join(argv)]


COMMAND_HANDLERS: dict[str, Callable[[argparse.Namespace], None]] = {
    "prompt": prompt_command_run,
    "json": json_command_run,
    "tool": tool_command_run,
    "chat": chat_command_run,
    "clear": clear_command_run,
    "sessions": sessions_command_run,
    "stats": stats_command_run,
    "status": status_command_run,
    "summarize": summarize_command_run,
    "doctor": doctor_command_run,
    "web-fetch": web_fetch_command_run,
    "web-search": web_search_command_run,
    "web-chat": web_chat_command_run,
    "web-cleanup": web_cleanup_command_run,
    "migrate": migrate_command_run,
    "repair": repair_command_run,
    "read-file": read_file_command_run,
    "file-chat": file_chat_command_run,
    "shell": shell_command_run,
    "workspace-create": workspace_create_command_run,
    "workspace-list": workspace_list_command_run,
    "workspace-show": workspace_show_command_run,
    "workspace-add-session": workspace_add_session_command_run,
    "workspace-add-file": workspace_add_file_command_run,
    "workspace-add-web-artifact": workspace_add_web_artifact_command_run,
    "workspace-chat": workspace_chat_command_run,
    "profile-show": profile_show_command_run,
    "profile-enable": profile_enable_command_run,
    "profile-disable": profile_disable_command_run,
    "profile-delete": profile_delete_command_run,
    "profile-set": profile_set_command_run,
    "profile-clear": profile_clear_command_run,
}


def parser_build() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Local AI CLI")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show full traceback on errors",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show structured log events in terminal",
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="AI data directory under ~/ai (default: data)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_prompt = subparsers.add_parser("prompt", help="Run a plain prompt")
    p_prompt.add_argument("text", help="Prompt text")

    subparsers.add_parser("json", help="Run structured JSON test")

    p_tool = subparsers.add_parser("tool", help="Run tool-calling test")
    p_tool.add_argument("path", help="Path for directory_list tool")

    p_chat = subparsers.add_parser("chat", help="Run chat with session memory")
    p_chat.add_argument("text", help="Chat prompt text")
    p_chat.add_argument("--session", default=None, help="Session name")

    p_clear = subparsers.add_parser("clear", help="Clear session memory")
    p_clear.add_argument("--session", default=None, help="Session name")

    subparsers.add_parser("sessions", help="List sessions")

    p_stats = subparsers.add_parser("stats", help="Show session stats")
    p_stats.add_argument("--session", default=None, help="Session name")

    subparsers.add_parser("status", help="Show AI runtime status")

    p_summarize = subparsers.add_parser(
        "summarize",
        help="Explicitly summarize one session or all sessions",
    )
    p_summarize.add_argument("--session", default=None, help="Session name")
    p_summarize.add_argument(
        "--all",
        action="store_true",
        help="Explicitly summarize all sessions",
    )

    subparsers.add_parser("doctor", help="Run local runtime checks")

    p_web_fetch = subparsers.add_parser(
        "web-fetch",
        help="Fetch one explicit URL and save a web artifact",
    )
    p_web_fetch.add_argument("url", help="URL to fetch")

    p_web_search = subparsers.add_parser(
        "web-search",
        help="Search the web and fetch top results",
    )
    p_web_search.add_argument("query", help="Search query")
    p_web_search.add_argument("--limit", type=int, default=3, help="Max results")

    p_web_chat = subparsers.add_parser(
        "web-chat",
        help="Answer a question using one explicit URL or a web search query",
    )
    p_web_chat.add_argument("question", help="Question to answer")

    source_group = p_web_chat.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--url", help="URL to fetch and use")
    source_group.add_argument("--query", help="Search query to fetch and use")

    p_web_chat.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Max search results when using --query (default: 3)",
    )

    p_web_cleanup = subparsers.add_parser(
        "web-cleanup",
        help="Clean up old web artifacts",
    )
    p_web_cleanup.add_argument(
        "--days",
        type=int,
        default=7,
        help="Remove artifacts older than N days (default: 7)",
    )
    p_web_cleanup.add_argument(
        "--delete",
        action="store_true",
        help="Actually delete files (default: dry run)",
    )

    p_migrate = subparsers.add_parser(
        "migrate",
        help="Normalize and rewrite one session or all sessions",
    )
    p_migrate.add_argument("--session", default=None, help="Session name")
    p_migrate.add_argument("--all", action="store_true", help="Migrate all sessions")
    p_migrate.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without writing files",
    )

    p_repair = subparsers.add_parser(
        "repair",
        help="Repair one session file conservatively",
    )
    p_repair.add_argument("--session", default=None, help="Session name")
    p_repair.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be repaired without writing files",
    )

    p_read_file = subparsers.add_parser(
        "read-file",
        help="Read one explicit local file",
    )
    p_read_file.add_argument("path")
    p_read_file.add_argument("--max-chars", type=int, default=None)

    p_file_chat = subparsers.add_parser(
        "file-chat",
        help="Answer a question using one explicit local file",
    )
    p_file_chat.add_argument("path")
    p_file_chat.add_argument("question")

    p_shell = subparsers.add_parser(
        "shell",
        help="Run interactive local-ai shell",
    )
    p_shell.add_argument(
        "--small",
        action="store_true",
        help="Use small model for faster interactive shell responses",
    )

    p_shell.add_argument(
        "--profile",
        default=None,
        help="Profile key to load for shell startup",
    )

    p_ws_create = subparsers.add_parser(
        "workspace-create",
        help="Create a workspace",
    )
    p_ws_create.add_argument("name")

    subparsers.add_parser(
        "workspace-list",
        help="List workspaces",
    )

    p_ws_show = subparsers.add_parser(
        "workspace-show",
        help="Show workspace",
    )
    p_ws_show.add_argument("name")

    p_ws_add_session = subparsers.add_parser(
        "workspace-add-session",
        help="Add a session reference to a workspace",
    )
    p_ws_add_session.add_argument("workspace")
    p_ws_add_session.add_argument("session")

    p_ws_add_file = subparsers.add_parser(
        "workspace-add-file",
        help="Add a file reference to a workspace",
    )
    p_ws_add_file.add_argument("workspace")
    p_ws_add_file.add_argument("path")

    p_ws_add_web_artifact = subparsers.add_parser(
        "workspace-add-web-artifact",
        help="Add a web artifact reference to a workspace",
    )
    p_ws_add_web_artifact.add_argument("workspace")
    p_ws_add_web_artifact.add_argument("artifact_path")

    p_workspace_chat = subparsers.add_parser(
        "workspace-chat",
        help="Answer a question using explicit workspace references",
    )
    p_workspace_chat.add_argument("workspace")
    p_workspace_chat.add_argument("question")

    p_profile_show = subparsers.add_parser(
        "profile-show",
        help="Show stored profile",
    )

    p_profile_show.add_argument("--profile", default=None)
    p_profile_enable = subparsers.add_parser(
        "profile-enable",
        help="Enable a profile",
    )

    p_profile_enable.add_argument("--profile", default=None)
    p_profile_disable = subparsers.add_parser(
        "profile-disable",
        help="Disable a profile",
    )

    p_profile_disable.add_argument("--profile", default=None)
    p_profile_delete = subparsers.add_parser(
        "profile-delete",
        help="Delete stored profile",
    )

    p_profile_set = subparsers.add_parser(
        "profile-set",
        help="Set a profile value",
    )

    p_profile_set.add_argument("key")
    p_profile_set.add_argument("value")
    p_profile_set.add_argument("--profile", default=None)
    p_profile_clear = subparsers.add_parser(
        "profile-clear",
        help="Clear a profile value",
    )

    p_profile_clear.add_argument("key")
    p_profile_clear.add_argument("--profile", default=None)

    return parser


# WHY:
# main() is the CLI boundary for argument parsing, command dispatch, and
# command-level logging. This keeps one clear entrypoint where cross-cutting
# concerns like logging and later top-level error handling can live.
def main() -> None:
    """Parse arguments, dispatch the command, and handle top-level logging."""
    parser = parser_build()
    #args = parser.parse_args()
    argv = argv_normalize(sys.argv[1:])
    args = parser.parse_args(argv)

    os.environ["OWB_DATA_DIR"] = args.data_dir

    if args.verbose:
        os.environ["OWB_VERBOSE"] = "1"

    command = args.command
    handler = COMMAND_HANDLERS.get(command)

    if handler is None:
        raise RuntimeError(f"Unknown command: {command}")

    started_at = time.perf_counter()

    log_event(
        "command.start",
        command=command,
    )

    try:
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

        if getattr(args, "debug", False):
            import traceback
            traceback.print_exc()
        else:
            fail(f"error: {exc}")

        sys.exit(1)

    log_event(
        "command.end",
        command=command,
        event_outcome="success",
        elapsed_ms=int((time.perf_counter() - started_at) * 1000),
    )


if __name__ == "__main__":
    main()
