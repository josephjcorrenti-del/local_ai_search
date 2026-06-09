from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import time

from local_ai_search.config import ConfigError, SUPPORTED_SEARCH_PROVIDERS, load_config
from local_ai_search.evidence import (
    EvidenceError,
    evidence_char_count,
    format_evidence_preview,
    load_evidence_from_local_search,
)
from local_ai_search.logging import elapsed_ms_get, log_event
from local_ai_search.output import fail_print, info_print, pass_print
from local_ai_search.paths import ensure_runtime_dirs, get_paths


def cmd_status(args: argparse.Namespace) -> int:
    started_at = time.perf_counter()
    log_event("status.start", command="status", event_outcome="start")

    try:
        paths = ensure_runtime_dirs()

        info_print("local_ai_search status")
        print()
        info_print("paths")
        print(f"[*]   repo_root:    {paths.repo_root}")
        print(f"[*]   data_root:    {paths.data_root}")
        print(f"[*]   log_dir:      {paths.log_dir}")
        print(f"[*]   run_log:      {paths.run_log}")
        print(f"[*]   evidence_dir: {paths.evidence_dir}")
        print(f"[*]   exports_dir:  {paths.exports_dir}")

        exit_code = 0

        if not args.self_only:
            exit_code = _ecosystem_status_run()

        log_event(
            "status.done",
            command="status",
            event_outcome="success" if exit_code == 0 else "failure",
            elapsed_ms=elapsed_ms_get(started_at),
        )

        return exit_code
    except Exception as exc:
        log_event(
            "status.error",
            level="ERROR",
            command="status",
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            elapsed_ms=elapsed_ms_get(started_at),
        )
        raise




def _check_writable_dir(path) -> bool:
    path.mkdir(parents=True, exist_ok=True)
    test_file = path / ".write_test"
    test_file.write_text("ok", encoding="utf-8")
    test_file.unlink()
    return True


def cmd_doctor(args: argparse.Namespace) -> int:
    started_at = time.perf_counter()
    log_event("doctor.start", command="doctor", event_outcome="start")

    try:
        paths = ensure_runtime_dirs()

        info_print("local_ai_search doctor")
        print()

        checks = [
            ("data_root writable", paths.data_root),
            ("log_dir writable", paths.log_dir),
            ("evidence_dir writable", paths.evidence_dir),
            ("exports_dir writable", paths.exports_dir),
        ]

        for label, path in checks:
            _check_writable_dir(path)
            pass_print(label)

        try:
            config = load_config()
        except ConfigError as exc:
            fail_print(f"config loaded: {exc}")
            log_event(
                "doctor.error",
                level="ERROR",
                command="doctor",
                event_outcome="failure",
                error_message=str(exc),
                error_type=type(exc).__name__,
                elapsed_ms=elapsed_ms_get(started_at),
            )
            return 1

        pass_print("config loaded")
        pass_print(f"search_provider valid: {config.search_provider}")
        print()
        info_print("doctor passed")

        exit_code = 0

        if not args.self_only:
            exit_code = _ecosystem_doctor_run()

        log_event(
            "doctor.done",
            command="doctor",
            event_outcome="success" if exit_code == 0 else "failure",
            elapsed_ms=elapsed_ms_get(started_at),
        )

        return exit_code
    except Exception as exc:
        log_event(
            "doctor.error",
            level="ERROR",
            command="doctor",
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            elapsed_ms=elapsed_ms_get(started_at),
        )
        raise


def cmd_config_show(_args: argparse.Namespace) -> int:
    started_at = time.perf_counter()
    log_event("config_show.start", command="config-show", event_outcome="start")

    try:
        config = load_config()

        info_print("local_ai_search config")
        print()
        print(f"[*] search_provider: {config.search_provider}")
        print()
        info_print("supported providers")
        for provider in SUPPORTED_SEARCH_PROVIDERS:
            info_print(f"  - {provider}")

        log_event(
            "config_show.done",
            command="config-show",
            event_outcome="success",
            elapsed_ms=elapsed_ms_get(started_at),
        )
        return 0
    except Exception as exc:
        log_event(
            "config_show.error",
            level="ERROR",
            command="config-show",
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            elapsed_ms=elapsed_ms_get(started_at),
        )
        raise


def cmd_inspect_evidence(args: argparse.Namespace) -> int:
    started_at = time.perf_counter()
    log_event("evidence.inspect.start", command="inspect-evidence", event_outcome="start")

    try:
        evidence = load_evidence_from_local_search(
            Path(args.path),
            limit=args.limit,
            max_chars=args.max_chars,
        )

        if args.json:
            print(json.dumps(evidence, indent=2))
        else:
            info_print("local_ai_search evidence")
            print()
            print(f"[*] retrieval_version: {evidence.get('retrieval_version')}")
            print(f"[*] artifact_type:      {evidence.get('artifact_type')}")
            print(f"[*] provider:           {evidence.get('provider')}")
            print(f"[*] query:              {evidence.get('query')}")
            print(f"[*] result_count:       {len(evidence.get('results', []))}")
            print(f"[*] char_count:         {evidence_char_count(evidence)}")
            print()
            print(format_evidence_preview(evidence))

        log_event(
            "evidence.inspect.done",
            command="inspect-evidence",
            event_outcome="success",
            elapsed_ms=elapsed_ms_get(started_at),
            result_count=len(evidence.get("results", [])),
            #char_count=evidence_char_count(evidence),
        )
        return 0

    except EvidenceError as exc:
        fail_print(str(exc))
        log_event(
            "evidence.inspect.error",
            level="ERROR",
            command="inspect-evidence",
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
            elapsed_ms=elapsed_ms_get(started_at),
        )
        return 1


def _external_command_run(command: list[str]) -> int:
    print()
    info_print(" ".join(command))

    try:
        result = subprocess.run(command, check=False)
    except FileNotFoundError:
        fail_print(f"command not found: {command[0]}")
        return 1

    return result.returncode


def _ecosystem_status_run() -> int:
    exit_code = 0
    exit_code = max(exit_code, _external_command_run(["local-search", "status"]))
    exit_code = max(exit_code, _external_command_run(["local-ai", "status"]))
    return exit_code


def _ecosystem_doctor_run() -> int:
    exit_code = 0
    exit_code = max(exit_code, _external_command_run(["local-search", "doctor"]))
    exit_code = max(exit_code, _external_command_run(["local-ai", "doctor"]))
    return exit_code


def _ecosystem_config_show_run() -> int:
    exit_code = 0
    exit_code = max(exit_code, _external_command_run(["local-search", "config-show"]))
    exit_code = max(exit_code, _external_command_run(["local-ai", "config-show"]))
    return exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="local-ai-search")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=cmd_status)

    status_parser.add_argument(
        "--self",
        action="store_true",
        dest="self_only",
        help="Check only local_ai_search.",
    )

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.set_defaults(func=cmd_doctor)

    doctor_parser.add_argument(
        "--self",
        action="store_true",
        dest="self_only",
        help="Check only local_ai_search.",
    )

    config_show_parser = subparsers.add_parser("config-show")
    config_show_parser.set_defaults(func=cmd_config_show)

    inspect_evidence_parser = subparsers.add_parser("inspect-evidence")
    inspect_evidence_parser.add_argument("path")
    inspect_evidence_parser.add_argument("--limit", type=int, default=5)
    inspect_evidence_parser.add_argument("--max-chars", type=int, default=4000)
    inspect_evidence_parser.set_defaults(func=cmd_inspect_evidence)

    inspect_evidence_parser.add_argument(
        "--json",
        action="store_true",
        help="Print validated evidence JSON.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
