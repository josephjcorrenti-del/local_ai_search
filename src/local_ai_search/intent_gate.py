from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from local_ai.memory import session_load, session_turns_get


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


IntentRoute = Literal[
    "model_only",
    "retrieve",
    "insufficient_context",
]


@dataclass(frozen=True)
class IntentDecision:
    route: IntentRoute
    reason: str

    @property
    def needs_retrieval(self) -> bool:
        return self.route == "retrieve"


def session_context_available(session_name: str | None) -> bool:
    if not session_name:
        return False

    if session_turns_get(session_name):
        return True

    session = session_load(session_name)
    return bool(session.get("summary"))


def decide_intent(
    query: str,
    *,
    mode: str = "integrated",
    session_name: str | None = None,
) -> IntentDecision:
    normalized = " ".join(query.lower().split())

    if mode == "web_only":
        return IntentDecision("retrieve", "web_only mode requires retrieval")

    if mode == "ai_only":
        return IntentDecision("model_only", "ai_only mode skips retrieval")

    if any(pattern in normalized for pattern in _CURRENT_PATTERNS):
        return IntentDecision("retrieve", "query appears freshness-sensitive")

    if any(pattern in normalized for pattern in _SESSION_CONTEXT_PATTERNS):
        if session_context_available(session_name):
            return IntentDecision(
                "model_only",
                "query appears answerable from session context",
            )

        return IntentDecision(
            "insufficient_context",
            "query refers to conversation context but no usable session context is available",
        )

    return IntentDecision("retrieve", "default integrated mode retrieves evidence")
