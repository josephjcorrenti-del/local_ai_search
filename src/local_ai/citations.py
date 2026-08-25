from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


_INLINE_REFERENCE_PATTERN = re.compile(r"\[(\d+)\]")


@dataclass(frozen=True)
class CitationValidation:
    cited_ranks: tuple[int, ...]
    invalid_ranks: tuple[int, ...]
    citation_required: bool

    @property
    def citation_missing(self) -> bool:
        return self.citation_required and not self.cited_ranks

    @property
    def valid(self) -> bool:
        return not self.citation_missing and not self.invalid_ranks


def citation_ranks_get(answer: str) -> tuple[int, ...]:
    return tuple(
        int(match.group(1))
        for match in _INLINE_REFERENCE_PATTERN.finditer(answer)
    )


def citation_validation_get(
    answer: str,
    allowed_ranks: Iterable[int],
    *,
    citation_required: bool,
) -> CitationValidation:
    allowed = set(allowed_ranks)
    cited = citation_ranks_get(answer)

    invalid = tuple(
        sorted({
            rank
            for rank in cited
            if rank not in allowed
        })
    )

    return CitationValidation(
        cited_ranks=cited,
        invalid_ranks=invalid,
        citation_required=citation_required,
    )


def citation_repair_prompt_get(allowed_ranks: Iterable[int]) -> str:
    references = " ".join(
        f"[{rank}]"
        for rank in sorted(set(allowed_ranks))
    )

    return (
        "Revise the draft answer so every factual claim based on the selected "
        "evidence has an inline reference immediately after the claim. "
        f"Use only these references: {references}. "
        "Use separate references such as [1][3], never combined references "
        "such as [1, 3]. Remove or qualify claims that the evidence does not "
        "support. Preserve the answer's meaning and return only the revised answer."
    )
