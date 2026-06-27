from __future__ import annotations

from typing import Literal


EvidenceSourceType = Literal[
    "workspace",
    "session",
    "file",
    "web_artifact",
    "search_result",
    "model_knowledge",
]


EVIDENCE_SOURCE_TYPES: tuple[str, ...] = (
    "workspace",
    "session",
    "file",
    "web_artifact",
    "search_result",
    "model_knowledge",
)


def evidence_source_type_validate(value: str) -> str:
    if value not in EVIDENCE_SOURCE_TYPES:
        supported = ", ".join(EVIDENCE_SOURCE_TYPES)
        raise ValueError(f"unsupported evidence source type: {value} supported: {supported}")

    return value