"""Document ingest helpers for local_search."""

from __future__ import annotations


import json
from pathlib import Path
from typing import Any
import time

from local_search.artifacts import artifact_load
from local_search.log import log_event
from local_search.storage import (
    chunk_insert,
    document_exists,
    document_insert,
    source_upsert,
)
from local_search.text import chunk_text, sha256_hex


def file_index(path: Path) -> dict[str, Any]:
    """Index a local text file and return a structured ingest result."""
    log_event(
        "index.file.start",
        command="index-file",
        path=str(path),
    )

    if not path.exists():
        log_event(
            "index.file.error",
            command="index-file",
            path=str(path),
            event_outcome="failure",
            error_message="file does not exist",
        )
        return {
            "status": "missing",
            "index_path": str(path),
        }

    if not path.is_file():
        log_event(
            "index.file.error",
            command="index-file",
            path=str(path),
            event_outcome="failure",
            error_message="not a file",
        )
        return {
            "status": "not_file",
            "index_path": str(path),
        }

    resolved_path = path.resolve()
    text = path.read_text(encoding="utf-8")
    content_sha256 = sha256_hex(text)

    if document_exists(content_sha256):
        log_event(
            "index.file.skip_unchanged",
            command="index-file",
            path=str(path),
            event_outcome="success",
        )
        return {
            "status": "unchanged",
            "index_path": str(path),
            "content_sha256": content_sha256,
        }

    source_id = f"src_{sha256_hex(str(resolved_path))}"
    document_id = f"doc_{content_sha256}"

    source_upsert(
        source_id=source_id,
        source_type="file",
        index_path=str(resolved_path),
    )

    document_insert(
        document_id=document_id,
        source_id=source_id,
        document_type="text",
        index_path=str(resolved_path),
        raw_ref=str(resolved_path),
        content_sha256=content_sha256,
        size_bytes=path.stat().st_size,
    )

    chunks = chunk_text(text)

    for chunk in chunks:
        chunk_id = f"chunk_{document_id}_{chunk['chunk_index']}"

        chunk_insert(
            chunk_id=chunk_id,
            document_id=document_id,
            chunk_index=chunk["chunk_index"],
            content=chunk["content"],
            start_char=chunk["start_char"],
            end_char=chunk["end_char"],
            index_path=str(resolved_path),
        )

    log_event(
        "index.file.done",
        command="index-file",
        path=str(path),
        document_id=document_id,
        source_id=source_id,
        event_outcome="success",
    )

    return {
        "status": "indexed",
        "index_path": str(path),
        "resolved_index_path": str(resolved_path),
        "document_id": document_id,
        "source_id": source_id,
        "content_sha256": content_sha256,
        "chunk_count": len(chunks),
    }

def web_artifact_index(path: Path) -> dict[str, Any]:
    """Index a saved web artifact JSON file."""
    started = time.perf_counter()
    log_event(
        "index.web_artifact.start",
        command="index-web-artifact",
        path=str(path),
    )

    if not path.exists():
        return {
            "status": "missing",
            "index_path": str(path),
        }

    if not path.is_file():
        return {
            "status": "not_file",
            "index_path": str(path),
        }

    artifact = artifact_load(path)

    url = artifact.get("url")
    title = artifact.get("title")
    content_text = artifact.get("content_text", "")

    if not content_text.strip():
        return {
            "status": "empty",
            "index_path": str(path),
        }

    content_sha256 = sha256_hex(content_text)

    if document_exists(content_sha256):
        log_event(
            "index.web_artifact.skip_unchanged",
            command="index-web-artifact",
            path=str(path),
            event_outcome="success",
        )

        return {
            "status": "unchanged",
            "index_path": str(path),
            "content_sha256": content_sha256,
        }

    resolved_path = path.resolve()

    source_id = f"src_{sha256_hex(str(resolved_path))}"
    document_id = f"doc_{content_sha256}"

    source_upsert(
        source_id=source_id,
        source_type="web_artifact",
        index_path=str(resolved_path),
        url=url,
        title=title,
    )

    document_insert(
        document_id=document_id,
        source_id=source_id,
        document_type="web_page",
        index_path=str(resolved_path),
        raw_ref=str(resolved_path),
        content_sha256=content_sha256,
        size_bytes=path.stat().st_size,
    )

    chunks = chunk_text(content_text)

    results = artifact.get("results")

    if isinstance(results, list) and results:
        chunks = []

        for index, result in enumerate(results):
            title = str(result.get("title") or "").strip()
            url = str(result.get("url") or "").strip()
            snippet = str(result.get("snippet") or "").strip()

            content = "\n".join(
                part for part in [title, url, snippet] if part
            )

            if not content.strip():
                continue

            chunk_id = f"chunk_{document_id}_{index}"

            chunk_insert(
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=index,
                content=content,
                start_char=0,
                end_char=len(content),
                index_path=str(resolved_path),
                title=title or None,
                url=url or None,
            )

            chunks.append(
                {
                    "chunk_index": index,
                    "content": content,
                }
            )
    else:
        chunks = chunk_text(content_text)

        for chunk in chunks:
            chunk_id = f"chunk_{document_id}_{chunk['chunk_index']}"

            chunk_insert(
                chunk_id=chunk_id,
                document_id=document_id,
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
                start_char=chunk["start_char"],
                end_char=chunk["end_char"],
                index_path=str(resolved_path),
            )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    log_event(
        "index.web_artifact.done",
        command="index-web-artifact",
        path=str(path),
        document_id=document_id,
        source_id=source_id,
        event_outcome="success",
        elapsed_ms = elapsed_ms,
    )

    return {
        "status": "indexed",
        "index_path": str(path),
        "document_id": document_id,
        "source_id": source_id,
        "chunk_count": len(chunks),
    }