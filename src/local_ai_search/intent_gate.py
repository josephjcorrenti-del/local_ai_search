from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentDecision:
    needs_retrieval: bool
    reason: str


_SESSION_CONTEXT_PATTERNS = (
    "what did i just",
    "what did i tell you",
    "did i just tell you",
    "did i tell you",
    "what did we just",
    "what did we say",
    "what was my",
    "what is my",
    "remind me what",
    "earlier",
    "above",
    "previous",
)

_CURRENT_PATTERNS = (
    "latest",
    "recent",
    "current",
    "today",
    "yesterday",
    "this week",
    "this month",
    "new release",
    "released",
    "announced",
)


def decide_intent(
    query: str,
    *,
    mode: str = "integrated",
    session_name: str | None = None,
) -> IntentDecision:
    normalized = " ".join(query.lower().split())

    if mode == "web_only":
        return IntentDecision(True, "web_only mode requires retrieval")

    if mode == "ai_only":
        return IntentDecision(False, "ai_only mode skips retrieval")

    if any(pattern in normalized for pattern in _CURRENT_PATTERNS):
        return IntentDecision(True, "query appears freshness-sensitive")

    if session_name and any(pattern in normalized for pattern in _SESSION_CONTEXT_PATTERNS):
        return IntentDecision(False, "query appears answerable from session context")

    return IntentDecision(True, "default integrated mode retrieves evidence")
