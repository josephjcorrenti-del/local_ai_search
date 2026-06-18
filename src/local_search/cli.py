"""CLI entry point for local_search."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

from local_search.ingest import file_index, web_artifact_index
from local_search.log import log_event
from local_search.paths import (
    ARTIFACTS_DIR,
    DATA_ROOT,
    DB_PATH,
    EXPORTS_DIR,
    LOG_DIR,
    RUN_LOG,
    ensure_app_dirs,
)
from local_search.output import (
    info_print,
    pass_print,
    fail_print,
)
from local_search.retrieval import artifact_evidence_get
from local_search.storage import (
    counts_get,
    document_inspect_get,
    fts5_available_check,
    schema_init,
    schema_version_get,
    search_get,
    chunk_window_command,
    artifact_index_purge,
    purge_artifacts_command,
)
from local_search.web_search import web_search


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-search",
        description="Local-first search engine for files and web artifacts.",
    )

    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Show local_search status.")
    status_parser.set_defaults(handler=lambda args: status_command())

    doctor_parser = subparsers.add_parser("doctor", help="Run local_search health checks.")
    doctor_parser.set_defaults(handler=lambda args: doctor_command())

    index_file_parser = subparsers.add_parser(
        "index-file",
        help="Index a local text file.",
    )
    index_file_parser.add_argument("path")
    index_file_parser.set_defaults(handler=lambda args: index_file_command(args.path))

    search_parser = subparsers.add_parser(
        "search",
        help="Search indexed content.",
    )
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--json", action="store_true")
    search_parser.set_defaults(
        handler=lambda args: search_command(
            args.query,
            limit=args.limit,
            json_output=args.json,
        )
    )

    inspect_parser = subparsers.add_parser(
        "inspect-document",
        help="Inspect an indexed document.",
    )
    inspect_parser.add_argument("document_id")
    inspect_parser.set_defaults(
        handler=lambda args: inspect_document_command(args.document_id)
    )

    index_web_artifact_parser = subparsers.add_parser(
        "index-web-artifact",
        help="Index a saved web artifact JSON file.",
    )
    index_web_artifact_parser.add_argument("path")
    index_web_artifact_parser.set_defaults(
        handler=lambda args: index_web_artifact_command(args.path)
    )

    search_parser.add_argument("--local-only", action="store_true")
    search_parser.set_defaults(
        handler=lambda args: search_command(
            args.query,
            limit=args.limit,
            json_output=args.json,
            local_only=args.local_only,
        )
    )

    chunk_window_parser = subparsers.add_parser(
        "chunk-window",
        help="Inspect neighboring chunks around a chunk index.",
    )

    chunk_window_parser.add_argument("document_id")
    chunk_window_parser.add_argument("chunk_index", type=int)
    chunk_window_parser.add_argument("--radius", type=int, default=1)

    chunk_window_parser.set_defaults(
        handler=lambda args: chunk_window_command(
            args.document_id,
            args.chunk_index,
            radius=args.radius,
        )
    )

    purge_artifact_parser = subparsers.add_parser(
        "purge-artifact",
        help="Delete an artifact and its indexed rows.",
    )
    purge_artifact_parser.add_argument("path")
    purge_artifact_parser.add_argument("--yes", action="store_true")
    purge_artifact_parser.set_defaults(
        handler=lambda args: purge_artifact_command(args.path, yes=args.yes)
    )

    purge_artifacts_parser = subparsers.add_parser(
        "purge-artifacts",
        help="Delete generated artifacts and indexed rows.",
    )
    purge_artifacts_parser.add_argument("--web", action="store_true")
    purge_artifacts_parser.add_argument("--yes", action="store_true")
    purge_artifacts_parser.set_defaults(
        handler=lambda args: purge_artifacts_command(
            web=args.web,
            yes=args.yes,
        )
    )

    evidence_parser = subparsers.add_parser(
        "evidence",
        help="Build an AI-ready evidence package from an artifact.",
    )

    evidence_parser.add_argument("path")
    evidence_parser.add_argument("--limit", type=int, default=5)
    evidence_parser.add_argument("--max-chars", type=int, default=4000)

    evidence_parser.set_defaults(
        handler=lambda args: evidence_command(
            args.path,
            limit=args.limit,
            max_chars=args.max_chars,
        )
    )

    return parser


def status_command() -> int:
    ensure_app_dirs()

    log_event("status.start", command="status")

    info_print("local_search status")
    print()
    info_print("paths")
    info_print(f"  data_root:     {DATA_ROOT}")
    info_print(f"  db_path:       {DB_PATH}")
    info_print(f"  log_dir:       {LOG_DIR}")
    info_print(f"  run_log:       {RUN_LOG}")
    info_print(f"  artifacts_dir: {ARTIFACTS_DIR}")
    info_print(f"  exports_dir:   {EXPORTS_DIR}")
    print()
    info_print("storage")
    info_print(f"  db_exists:     {DB_PATH.exists()}")
    info_print(f"  run_log_exists:{RUN_LOG.exists()}")

    counts = counts_get()
    schema_version = schema_version_get()

    info_print(f"schema_version: {schema_version}")
    info_print(f"sources:        {counts['sources']}")
    info_print(f"documents:      {counts['documents']}")
    info_print(f"chunks:         {counts['chunks']}")

    log_event("status.done", command="status", event_outcome="success")
    return 0


def doctor_command() -> int:
    ensure_app_dirs()

    log_event("doctor.start", command="doctor")

    try:
        schema_init()
        db_ok = DB_PATH.exists()
    except Exception as exc:
        db_ok = False
        log_event(
            "doctor.db.error",
            command="doctor",
            event_outcome="failure",
            error_message=str(exc),
            error_type=type(exc).__name__,
        )

    fts5_ok = fts5_available_check()

    checks = [
        ("data_root exists", DATA_ROOT.exists()),
        ("log_dir exists", LOG_DIR.exists()),
        ("artifacts_dir exists", ARTIFACTS_DIR.exists()),
        ("exports_dir exists", EXPORTS_DIR.exists()),
        ("log_dir writable", LOG_DIR.exists() and LOG_DIR.is_dir()),
        ("db exists or can be created", db_ok),
        ("FTS5 is available", fts5_ok),
    ]

    failed = False

    info_print("local_search doctor")
    print()

    for label, ok in checks:
        if ok:
            pass_print(label)
            log_event(
                "doctor.check.ok",
                command="doctor",
                event_outcome="success",
                path=str(DATA_ROOT),
            )
        else:
            failed = True
            fail_print(label)
            log_event(
                "doctor.check.fail",
                command="doctor",
                event_outcome="failure",
                error_message=label,
            )

    if failed:
        log_event("doctor.done", command="doctor", event_outcome="failure")
        return 1

    print()
    pass_print("doctor passed")
    log_event("doctor.done", command="doctor", event_outcome="success")
    return 0


def index_file_command(path_str: str) -> int:
    result = file_index(Path(path_str))

    if result["status"] == "missing":
        fail_print(f"file does not exist: {result['index_path']}")
        return 1

    if result["status"] == "not_file":
        fail_print(f"not a file: {result['index_path']}")
        return 1

    if result["status"] == "unchanged":
        info_print("unchanged file skipped")
        return 0

    pass_print(f"indexed {result['index_path']}")
    info_print(f"chunks: {result['chunk_count']}")
    return 0


def search_command(
    query: str,
    *,
    limit: int,
    json_output: bool,
    local_only: bool = False,
) -> int:
    log_event(
        "search.query.start",
        command="search",
        query=query,
    )

    search_started = time.perf_counter()

    schema_init()

    results = search_get(query, limit=limit)

    elapsed_ms = int((time.perf_counter() - search_started) * 1000)

    log_event(
        "search.query.done",
        command="search",
        query=query,
        event_outcome="success",
        result_count=len(results),
        elapsed_ms=elapsed_ms,
    )

    if json_output:
        print(json.dumps(results, indent=2))
        return 0

    info_print(f"local results for: {query}")
    print()

    if not results:
        info_print("no local results")

        if local_only:
            return 0

        info_print("searching web")
        print()

        web_result = web_search(query)

        if not web_result["results"]:
            info_print("no web results")
            return 0

        for index, result in enumerate(web_result["results"], start=1):
            print(f"{index}. {result['title']}")
            print(f"   url: {result['url']}")
            print(f"   snippet: {result['snippet']}")
            print()

        pass_print(f"saved web artifact: {web_result['artifact_path']}")

        index_result = web_artifact_index(Path(web_result["artifact_path"]))

        if index_result["status"] == "indexed":
            pass_print(f"indexed web artifact: {index_result['document_id']}")
            info_print(f"chunks: {index_result['chunk_count']}")
        elif index_result["status"] == "unchanged":
            info_print("web artifact already indexed")
        else:
            fail_print(f"web artifact auto-index failed: {index_result['status']}")

        return 0

    seen_documents = set()
    collapsed_results = []

    for result in results:
        document_id = result["document_id"]

        if result["source_type"] != "web_artifact":
            if document_id in seen_documents:
                continue
            seen_documents.add(document_id)

        collapsed_results.append(result)

    for index, result in enumerate(collapsed_results, start=1):
        display_title = result["title"] or result["index_path"] or result["url"]
        display_url = result["url"]

        print(f"{index}. {display_title}")

        if display_url:
            print(f"   url: {display_url}")
        else:
            print(f"   path: {result['index_path']}")

        print(f"   score: {result['score']}")
        print(f"   source: {result['source_type']}")
        print(f"   document_id: {result['document_id']}")
        print(f"   source_id: {result['source_id']}")
        print(f"   raw_ref: {result['raw_ref']}")
        print(f"   chunk_id: {result['chunk_id']}")
        print(f"   chunk_index: {result['chunk_index']}")
        print(f"   snippet: {result['snippet']}")
        print(f"   rank: {result['rank']}")
        print()

    return 0


def inspect_document_command(document_id: str) -> int:
    log_event(
        "document.inspect.start",
        command="inspect-document",
        document_id=document_id,
    )

    result = document_inspect_get(document_id)

    if result is None:
        fail_print(f"document not found: {document_id}")
        log_event(
            "document.inspect.done",
            command="inspect-document",
            document_id=document_id,
            event_outcome="failure",
            error_message="document not found",
        )
        return 1

    document = result["document"]
    chunks = result["chunks"]

    info_print("document")
    info_print(f"  document_id:    {document['document_id']}")
    info_print(f"  source_id:      {document['source_id']}")
    info_print(f"  source_type:    {document['source_type']}")
    info_print(f"  document_type:  {document['document_type']}")
    info_print(f"  index_path:     {document['index_path']}")
    info_print(f"  url:            {document['url']}")
    info_print(f"  raw_ref:        {document['raw_ref']}")
    info_print(f"  content_sha256: {document['content_sha256']}")
    info_print(f"  size_bytes:     {document['size_bytes']}")
    info_print(f"  created_at:     {document['created_at']}")
    info_print(f"  indexed_at:     {document['indexed_at']}")
    print()

    info_print("chunks")
    info_print(f"  chunk_count:    {len(chunks)}")

    for chunk in chunks:
        info_print(
            f"  {chunk['chunk_index']}: "
            f"{chunk['chunk_id']} "
            f"chars={chunk['start_char']}-{chunk['end_char']} "
            f"content_chars={chunk['content_chars']}"
        )

    log_event(
        "document.inspect.done",
        command="inspect-document",
        document_id=document_id,
        event_outcome="success",
    )

    return 0


def index_web_artifact_command(path_str: str) -> int:
    result = web_artifact_index(Path(path_str))

    if result["status"] == "missing":
        fail_print(f"artifact does not exist: {result['index_path']}")
        return 1

    if result["status"] == "not_file":
        fail_print(f"not a file: {result['index_path']}")
        return 1

    if result["status"] == "empty":
        fail_print(f"artifact has no content_text: {result['index_path']}")
        return 1

    if result["status"] == "unchanged":
        info_print("unchanged web artifact skipped")
        return 0

    pass_print(f"indexed web artifact {result['index_path']}")
    info_print(f"chunks: {result['chunk_count']}")
    return 0


def purge_artifact_command(path_str: str, *, yes: bool) -> int:
    candidate = Path(path_str).expanduser()
    artifacts_root = ARTIFACTS_DIR.resolve()

    if candidate.is_absolute():
        path = candidate.resolve()
    elif candidate.parts and candidate.parts[0] == "artifacts":
        path = (DATA_ROOT / candidate).resolve()
    else:
        path = (ARTIFACTS_DIR / candidate).resolve()


    if artifacts_root not in path.parents:
        fail_print(f"refusing to purge outside artifacts directory: {path}")
        return 1

    if not path.exists():
        fail_print(f"artifact does not exist: {path}")
        return 1

    if not path.is_file():
        fail_print(f"not an artifact file: {path}")
        return 1

    if not yes:
        fail_print("destructive purge requires --yes")
        return 1

    schema_init()
    result = artifact_index_purge(str(path))
    path.unlink()

    pass_print(f"purged artifact: {path}")
    info_print(f"documents_deleted: {result['documents_deleted']}")
    info_print(f"chunks_deleted: {result['chunks_deleted']}")
    info_print(f"fts_rows_deleted: {result['fts_rows_deleted']}")
    info_print(f"sources_deleted: {result['sources_deleted']}")
    return 0


def evidence_command(
    path_str: str,
    *,
    limit: int,
    max_chars: int,
) -> int:
    log_event(
        "evidence.build.start",
        command="evidence",
        path=path_str,
    )

    started = time.perf_counter()

    evidence = artifact_evidence_get(
        Path(path_str),
        limit=limit,
        max_chars=max_chars,
    )

    elapsed_ms = int((time.perf_counter() - started) * 1000)

    log_event(
        "evidence.build.done",
        command="evidence",
        path=path_str,
        event_outcome="success",
        result_count=len(evidence["results"]),
        elapsed_ms=elapsed_ms,
    )

    print(json.dumps(evidence, indent=2))
    return 0


def main() -> int:
    known_commands = {
        "status",
        "doctor",
        "index-file",
        "index-web-artifact",
        "search",
        "inspect-document",
        "chunk-window",
        "purge-artifact",
        "purge-artifacts",
        "evidence",
    }

    argv = sys.argv[1:]

    if not argv:
        parser = build_parser()
        parser.print_help()
        return 0

    first = argv[0]

    if first in {"-h", "--help"}:
        parser = build_parser()
        parser.print_help()
        return 0

    # Default smart/local search behavior.
    if first not in known_commands:
        smart_parser = argparse.ArgumentParser(add_help=False)
        smart_parser.add_argument("query", nargs="+")
        smart_parser.add_argument("--local-only", action="store_true")

        smart_args = smart_parser.parse_args(argv)

        return search_command(
            " ".join(smart_args.query),
            limit=10,
            json_output=False,
            local_only=smart_args.local_only,
        )

    parser = build_parser()
    args = parser.parse_args()

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0

    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
