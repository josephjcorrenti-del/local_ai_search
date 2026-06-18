from __future__ import annotations

"""SQLite storage helpers for local_search."""

import sqlite3
from pathlib import Path
from typing import Any

from local_search.config import SCHEMA_VERSION
from local_search.paths import ARTIFACTS_DIR, DB_PATH, ensure_app_dirs
from local_search.text import chunk_snippet_build
from local_search.output import info_print, fail_print, pass_print

FTS_STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "or",
    "the",
    "to",
}


def fts_query_escape(query: str) -> str:
    """Return a safe FTS5 query for meaningful terms in any order."""
    raw_terms = query.split()

    filtered_terms = [
        term
        for term in raw_terms
        if term.lower() not in FTS_STOP_WORDS
    ]

    terms = filtered_terms or raw_terms

    escaped_terms = []

    for term in terms:
        escaped = term.replace('"', '""')
        escaped_terms.append(f'"{escaped}"')

    return " ".join(escaped_terms)


def connection_get(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection for the search database."""
    ensure_app_dirs()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def fts5_available_check() -> bool:
    """Return True when SQLite FTS5 is available."""
    with sqlite3.connect(":memory:") as conn:
        try:
            conn.execute("CREATE VIRTUAL TABLE fts_test USING fts5(content)")
            return True
        except sqlite3.OperationalError:
            return False


def schema_init(db_path: Path = DB_PATH) -> None:
    """Initialize the local_search SQLite schema."""
    with connection_get(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER NOT NULL,
                applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                index_path TEXT,
                url TEXT,
                title TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                metadata_json TEXT
            );

            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                title TEXT,
                index_path TEXT,
                url TEXT,
                content_sha256 TEXT NOT NULL,
                size_bytes INTEGER,
                raw_ref TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                indexed_at TEXT,
                metadata_json TEXT,
                FOREIGN KEY(source_id) REFERENCES sources(source_id)
            );

            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id TEXT NOT NULL UNIQUE,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                start_char INTEGER,
                end_char INTEGER,
                token_count INTEGER,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(document_id) REFERENCES documents(document_id)
            );

            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                title,
                index_path,
                url,
                content
            );
            """
        )

        existing = conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]
        if existing == 0:
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,),
            )


def counts_get(db_path: Path = DB_PATH) -> dict[str, int]:
    """Return basic database object counts."""
    if not db_path.exists():
        return {
            "sources": 0,
            "documents": 0,
            "chunks": 0,
        }

    with connection_get(db_path) as conn:
        return {
            "sources": int(conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]),
            "documents": int(conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]),
            "chunks": int(conn.execute("SELECT COUNT(*) FROM document_chunks").fetchone()[0]),
        }


def schema_version_get(db_path: Path = DB_PATH) -> int | None:
    """Return the current schema version, if initialized."""
    if not db_path.exists():
        return None

    with connection_get(db_path) as conn:
        row: Any = conn.execute(
            "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1"
        ).fetchone()

    if row is None:
        return None

    return int(row["version"])


def source_upsert(
    *,
    source_id: str,
    source_type: str,
    index_path: str | None = None,
    url: str | None = None,
    title: str | None = None,
) -> None:
    """Insert or replace a source record."""
    with connection_get() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sources (
                source_id,
                source_type,
                index_path,
                url,
                title
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                source_id,
                source_type,
                index_path,
                url,
                title,
            ),
        )


def document_exists(content_sha256: str) -> bool:
    """Return True if document content already exists."""
    with connection_get() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM documents
            WHERE content_sha256 = ?
            LIMIT 1
            """,
            (content_sha256,),
        ).fetchone()

    return row is not None


def document_insert(
    *,
    document_id: str,
    source_id: str,
    document_type: str,
    index_path: str,
    raw_ref: str,
    content_sha256: str,
    size_bytes: int,
) -> None:
    """Insert a document record."""
    with connection_get() as conn:
        conn.execute(
            """
            INSERT INTO documents (
                document_id,
                source_id,
                document_type,
                index_path,
                raw_ref,
                content_sha256,
                size_bytes,
                indexed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                document_id,
                source_id,
                document_type,
                index_path,
                raw_ref,
                content_sha256,
                size_bytes,
            ),
        )

def chunk_insert(
    *,
    chunk_id: str,
    document_id: str,
    chunk_index: int,
    content: str,
    start_char: int,
    end_char: int,
    index_path: str,
    title: str | None = None,
    url: str | None = None,
) -> None:
        """Insert a document chunk and FTS row."""
        with connection_get() as conn:
            cursor = conn.execute(
                """
                INSERT INTO document_chunks (
                    chunk_id,
                    document_id,
                    chunk_index,
                    content,
                    start_char,
                    end_char
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    document_id,
                    chunk_index,
                    content,
                    start_char,
                    end_char,
                ),
            )

            rowid = cursor.lastrowid

            conn.execute(
                """
                INSERT INTO chunks_fts (
                    rowid,
                    title,
                    index_path,
                    url,
                    content
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    rowid,
                    title,
                    index_path,
                    url,
                    content,
                ),
            )


def search_get(query: str, *, limit: int = 10) -> list[dict]:
    """Return ranked FTS search results."""
    with connection_get() as conn:
        rows = conn.execute(
            """
            SELECT
               documents.document_id,
               documents.source_id,
               documents.raw_ref,
               document_chunks.chunk_id,
               document_chunks.chunk_index,
               sources.source_type,
               documents.index_path,
               chunks_fts.url,
               chunks_fts.title,
               bm25(chunks_fts) AS score,
               document_chunks.content AS content
            FROM chunks_fts
            JOIN document_chunks ON chunks_fts.rowid = document_chunks.id
            JOIN documents ON document_chunks.document_id = documents.document_id
            JOIN sources ON documents.source_id = sources.source_id
            WHERE chunks_fts MATCH ?
            ORDER BY score
            LIMIT ?
            """,
            (fts_query_escape(query), limit),
        ).fetchall()

    results = []

    # for row in rows:
    #     result = dict(row)
    #     content = result.pop("content", "")
    #     result["snippet"] = chunk_snippet_build(content, query)
    #     results.append(result)

    for rank, row in enumerate(rows, start=1):
        result = dict(row)
        content = result.pop("content", "")
        result["rank"] = rank
        result["snippet"] = chunk_snippet_build(content, query)
        results.append(result)

    return results


def document_inspect_get(document_id: str) -> dict | None:
    """Return document, source, and chunk metadata for inspection."""
    with connection_get() as conn:
        document = conn.execute(
            """
            SELECT
                documents.document_id,
                documents.source_id,
                documents.document_type,
                documents.title,
                documents.index_path,
                documents.url,
                documents.content_sha256,
                documents.size_bytes,
                documents.raw_ref,
                documents.created_at,
                documents.indexed_at,
                documents.metadata_json,
                sources.source_type
            FROM documents
            JOIN sources ON documents.source_id = sources.source_id
            WHERE documents.document_id = ?
            """,
            (document_id,),
        ).fetchone()

        if document is None:
            return None

        chunks = conn.execute(
            """
            SELECT
                chunk_id,
                chunk_index,
                start_char,
                end_char,
                token_count,
                length(content) AS content_chars
            FROM document_chunks
            WHERE document_id = ?
            ORDER BY chunk_index
            """,
            (document_id,),
        ).fetchall()

    return {
        "document": dict(document),
        "chunks": [dict(row) for row in chunks],
    }


def chunk_window_get(
    document_id: str,
    chunk_index: int,
    *,
    radius: int = 1,
) -> list[dict]:
    """Return neighboring chunks around a document chunk."""
    start_index = max(chunk_index - radius, 0)
    end_index = chunk_index + radius

    with connection_get() as conn:
        rows = conn.execute(
            """
            SELECT
                chunk_id,
                document_id,
                chunk_index,
                content,
                start_char,
                end_char,
                token_count
            FROM document_chunks
            WHERE document_id = ?
              AND chunk_index BETWEEN ? AND ?
            ORDER BY chunk_index
            """,
            (document_id, start_index, end_index),
        ).fetchall()

    return [dict(row) for row in rows]


def chunk_window_command(
    document_id: str,
    chunk_index: int,
    *,
    radius: int,
) -> int:
    chunks = chunk_window_get(
        document_id,
        chunk_index,
        radius=radius,
    )

    if not chunks:
        fail_print("no chunks found")
        return 1

    info_print(f"document_id: {document_id}")
    info_print(f"chunk_index: {chunk_index}")
    info_print(f"radius: {radius}")
    print()

    for chunk in chunks:
        print(f"{chunk['chunk_index']}:")
        print("-" * 50)
        print(chunk["content"])
        print()

    return 0


def artifact_index_purge(raw_ref: str) -> dict[str, int]:
    """Remove indexed rows for an artifact raw_ref."""
    with connection_get() as conn:
        documents = conn.execute(
            """
            SELECT document_id, source_id
            FROM documents
            WHERE raw_ref = ?
            """,
            (raw_ref,),
        ).fetchall()

        document_ids = [row["document_id"] for row in documents]
        source_ids = [row["source_id"] for row in documents]

        if not document_ids:
            return {
                "documents_deleted": 0,
                "chunks_deleted": 0,
                "sources_deleted": 0,
                "fts_rows_deleted": 0,
            }

        chunk_rows = conn.execute(
            f"""
            SELECT id
            FROM document_chunks
            WHERE document_id IN ({",".join("?" for _ in document_ids)})
            """,
            document_ids,
        ).fetchall()

        chunk_rowids = [row["id"] for row in chunk_rows]

        fts_rows_deleted = 0
        if chunk_rowids:
            conn.execute(
                f"""
                DELETE FROM chunks_fts
                WHERE rowid IN ({",".join("?" for _ in chunk_rowids)})
                """,
                chunk_rowids,
            )
            fts_rows_deleted = len(chunk_rowids)

        conn.execute(
            f"""
            DELETE FROM document_chunks
            WHERE document_id IN ({",".join("?" for _ in document_ids)})
            """,
            document_ids,
        )

        conn.execute(
            f"""
            DELETE FROM documents
            WHERE document_id IN ({",".join("?" for _ in document_ids)})
            """,
            document_ids,
        )

        sources_deleted = 0
        for source_id in set(source_ids):
            remaining = conn.execute(
                """
                SELECT 1
                FROM documents
                WHERE source_id = ?
                LIMIT 1
                """,
                (source_id,),
            ).fetchone()

            if remaining is None:
                conn.execute(
                    "DELETE FROM sources WHERE source_id = ?",
                    (source_id,),
                )
                sources_deleted += 1

    return {
        "documents_deleted": len(document_ids),
        "chunks_deleted": len(chunk_rowids),
        "sources_deleted": sources_deleted,
        "fts_rows_deleted": fts_rows_deleted,
    }


def purge_artifacts_command(*, web: bool, yes: bool) -> int:
    if not web:
        fail_print("choose an artifact scope, for example: --web")
        return 1

    target_dir = ARTIFACTS_DIR / "web"

    if not target_dir.exists():
        info_print("no web artifacts directory")
        return 0

    artifact_paths = sorted(target_dir.glob("*.json"))

    info_print(f"web artifacts matched: {len(artifact_paths)}")

    if not yes:
        fail_print("destructive purge requires --yes")
        return 1

    schema_init()

    total_documents = 0
    total_chunks = 0
    total_fts = 0
    total_sources = 0
    files_deleted = 0

    for path in artifact_paths:
        result = artifact_index_purge(str(path.resolve()))

        path.unlink()

        files_deleted += 1
        total_documents += result["documents_deleted"]
        total_chunks += result["chunks_deleted"]
        total_fts += result["fts_rows_deleted"]
        total_sources += result["sources_deleted"]

    pass_print("purged web artifacts")
    info_print(f"files_deleted: {files_deleted}")
    info_print(f"documents_deleted: {total_documents}")
    info_print(f"chunks_deleted: {total_chunks}")
    info_print(f"fts_rows_deleted: {total_fts}")
    info_print(f"sources_deleted: {total_sources}")

    return 0