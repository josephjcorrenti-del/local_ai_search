from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

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
    limit: int = 5,
    max_chars: int = 4000,
) -> dict[str, Any]:
    result = subprocess.run(
        [
            "local-search",
            "evidence",
            str(path),
            "--limit",
            str(limit),
            "--max-chars",
            str(max_chars),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise EvidenceError(result.stderr.strip() or "local-search evidence failed")

    try:
        evidence = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise EvidenceError(f"invalid evidence JSON: {exc}") from exc

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
