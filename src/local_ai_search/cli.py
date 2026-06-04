from __future__ import annotations

import argparse

from local_ai_search.paths import ensure_runtime_dirs, get_paths


def cmd_status(_args: argparse.Namespace) -> int:
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
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="local-ai-search")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.set_defaults(func=cmd_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
