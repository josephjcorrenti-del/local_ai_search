from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


QueryMode = Literal["integrated", "ai_only", "web_only"]


class QueryRequest(BaseModel):
    query: str
    mode: QueryMode = "integrated"

    session: str | None = None
    workspace: str | None = None

    limit: int | None = None
    max_chars: int | None = None


class WorkspaceCreateRequest(BaseModel):
    name: str


class ApiError(BaseModel):
    type: str
    message: str


class IntentInfo(BaseModel):
    route: str
    reason: str


class RetrievalInfo(BaseModel):
    status: str
    reason: str | None = None


class QueryResponse(BaseModel):
    ok: bool
    mode: QueryMode
    query: str

    session: str
    workspace: str | None = None

    answer: str | None = None
    evidence: dict[str, Any] | None = None
    accounting: dict[str, Any] | None = None
    elapsed_ms: int
    error: ApiError | None = None
    intent: IntentInfo | None = None
    retrieval: RetrievalInfo | None = None
