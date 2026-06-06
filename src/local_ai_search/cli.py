from __future__ import annotations

import argparse
import time

from local_ai_search.config import ConfigError, SUPPORTED_SEARCH_PROVIDERS, load_config
from local_ai_search.logging import elapsed_ms_get, log_event
from local_ai_search.paths import ensure_runtime_dirs, get_paths


def cmd_status(_args: argparse.Namespace) -> int:
    started_at = time.perf_counter()
    log_event("status.start", command="status", event_outcome="start")

    try:
        paths = ensure_runtime_dirs()

        print("[*] local_ai_search status")
        print()
        print("[*] paths")
        print(f"[*]   repo_root:    {paths.repo_root}")
        print(f"[*]   data_root:    {paths.data_root}")
        print(f"[*]   log_dir:      {paths.log_dir}")
        print(f"[*]   run_log:      {paths.run_log}")
        print(f"[*]   evidence_dir: {paths.evidence_dir}")
        print(f"[*]   exports_dir:  {paths.exports_dir}")

        log_event(
            "status.done",
            command="status",
            event_outcome="success",
            elapsed_ms=elapsed_ms_get(started_at),
        )
        return 0
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


def cmd_doctor(_args: argparse.Namespace) -> int:
    started_at = time.perf_counter()
    log_event("doctor.start", command="doctor", event_outcome="start")

    try:
        paths = ensure_runtime_dirs()

        print("[*] local_ai_search doctor")
        print()

        checks = [
            ("data_root writable", paths.data_root),
            ("log_dir writable", paths.log_dir),
            ("evidence_dir writable", paths.evidence_dir),
            ("exports_dir writable", paths.exports_dir),
        ]

        for label, path in checks:
            _check_writable_dir(path)
            print(f"[✓] {label}")

        try:
            config = load_config()
        except ConfigError as exc:
            print(f"[x] config loaded: {exc}")
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

        print("[✓] config loaded")
        print(f"[✓] search_provider valid: {config.search_provider}")
        print()
        print("[*] doctor passed")

        log_event(
            "doctor.done",
            command="doctor",
            event_outcome="success",
            elapsed_ms=elapsed_ms_get(started_at),
        )
        return 0
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

        print("[*] local_ai_search config")
        print()
        print(f"[*] search_provider: {config.search_provider}")
        print()
        print("[*] supported providers")
        for provider in SUPPORTED_SEARCH_PROVIDERS:
            print(f"[*]   - {provider}")

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="local-ai-search")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=cmd_status)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.set_defaults(func=cmd_doctor)

    config_show_parser = subparsers.add_parser("config-show")
    config_show_parser.set_defaults(func=cmd_config_show)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
