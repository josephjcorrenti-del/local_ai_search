from __future__ import annotations

from pathlib import Path
from typing import Any

from local_ai_search.adapters.local_search import (
    LocalSearchAdapterError,
    get_evidence,
)
from local_ai_search.adapters import local_search
from local_ai_search.artifacts import latest_web_artifact_for_query
from local_ai_search.config import EVIDENCE_LIMIT, EVIDENCE_MAX_CHARS
from local_ai_search.intent_gate import IntentDecision
from local_ai_search.session_evidence import build_session_evidence
from local_ai_search.workspace_evidence import build_workspace_evidence

SUPPORTED_RETRIEVAL_VERSION = 1


class EvidenceError(Exception):
    pass


def evidence_char_count(evidence: dict[str, Any]) -> int:
    total = 0
    for result in evidence.get("results", []):
        total += len(str(result.get("title") or ""))
        total += len(str(result.get("url") or ""))
        total += len(str(result.get("snippet") or ""))
    return total


def load_evidence_from_local_search(
    path: Path,
    *,
    limit: int = EVIDENCE_LIMIT,
    max_chars: int = EVIDENCE_MAX_CHARS,
) -> dict[str, Any]:
    try:
        evidence = get_evidence(str(path), limit=limit, max_chars=max_chars)
    except LocalSearchAdapterError as exc:
        raise EvidenceError(str(exc)) from exc

    validate_evidence(evidence, max_chars=max_chars)
    return evidence


def validate_evidence(evidence: dict[str, Any], *, max_chars: int = 4000) -> None:
    required = [
        "retrieval_version",
        "artifact_type",
        "query",
        "provider",
        "fetched_at",
        "results",
    ]

    for field in required:
        if field not in evidence:
            raise EvidenceError(f"missing required evidence field: {field}")

    if evidence["retrieval_version"] != SUPPORTED_RETRIEVAL_VERSION:
        raise EvidenceError(
            f"unsupported retrieval_version: {evidence['retrieval_version']}"
        )

    if not isinstance(evidence["results"], list):
        raise EvidenceError("evidence results must be a list")

    for index, result in enumerate(evidence["results"], start=1):
        if not isinstance(result, dict):
            raise EvidenceError(f"evidence result {index} must be an object")

        for field in ["rank", "title", "url", "snippet"]:
            if field not in result:
                raise EvidenceError(f"evidence result {index} missing field: {field}")

    total_chars = evidence_char_count(evidence)
    if total_chars > max_chars:
        raise EvidenceError(
            f"evidence exceeds max chars: {total_chars} > {max_chars}"
        )


def format_evidence_preview(evidence: dict[str, Any]) -> str:
    lines: list[str] = []

    lines.append(f"query: {evidence.get('query')}")
    lines.append(f"provider: {evidence.get('provider')}")
    lines.append(f"retrieval_version: {evidence.get('retrieval_version')}")
    lines.append("")

    for result in evidence.get("results", []):
        lines.append(f"[{result.get('rank')}] {result.get('title')}")
        lines.append(str(result.get("url") or ""))
        lines.append(str(result.get("snippet") or ""))
        lines.append("")

    return "\n".join(lines).rstrip()


def resolve_evidence(
    query: str,
    *,
    decision: IntentDecision,
    session_name: str | None = None,
    workspace_name: str | None = None,
    limit: int | None = None,
    max_chars: int | None = None,
) -> dict[str, Any] | None:
    if decision.needs_retrieval:
        search_exit_code = local_search.search(query)
        if search_exit_code != 0:
            return None

        artifact_path = latest_web_artifact_for_query(query)

        return load_evidence_from_local_search(
            artifact_path,
            limit=limit or EVIDENCE_LIMIT,
            max_chars=max_chars or EVIDENCE_MAX_CHARS,
        )

    if workspace_name:
        return build_workspace_evidence(workspace_name)

    return build_session_evidence(session_name)