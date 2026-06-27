from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class EvidenceCounts:
    available_count: int
    evidence_count: int
    displayed_count: int

    def as_dict(self) -> dict[str, int]:
        return {
            "available_count": self.available_count,
            "evidence_count": self.evidence_count,
            "displayed_count": self.displayed_count,
        }


def evidence_counts_from_results(
    *,
    available_count: int,
    evidence_count: int,
    displayed_count: int,
) -> EvidenceCounts:
    if available_count < 0:
        raise ValueError("available_count cannot be negative")
    if evidence_count < 0:
        raise ValueError("evidence_count cannot be negative")
    if displayed_count < 0:
        raise ValueError("displayed_count cannot be negative")

    return EvidenceCounts(
        available_count=available_count,
        evidence_count=evidence_count,
        displayed_count=displayed_count,
    )


def available_count_from_artifact(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    results = data.get("results", [])

    if not isinstance(results, list):
        return 0

    return len(results)


def evidence_counts_for_web_artifact(
    path: Path,
    evidence: dict[str, Any],
    *,
    displayed_limit: int | None = None,
) -> EvidenceCounts:
    evidence_count = len(evidence.get("results", []))
    displayed_count = evidence_count

    if displayed_limit is not None:
        displayed_count = min(displayed_limit, evidence_count)

    return evidence_counts_from_results(
        available_count=available_count_from_artifact(path),
        evidence_count=evidence_count,
        displayed_count=displayed_count,
    )