from __future__ import annotations

import time

from fastapi import APIRouter

from local_ai_search.adapters import local_ai
from local_ai_search.api.schemas import QueryRequest, QueryResponse

router = APIRouter()


@router.get("/status")
def status() -> dict:
    return {
        "ok": True,
        "service": "local_ai_search",
        "version": "0.1",
        "checks": {
            "local_ai_search": True,
            "local_ai": None,
            "local_search": None,
        },
    }


@router.get("/config")
def config() -> dict:
    return {
        "ok": True,
        "config": {},
    }


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    started = time.perf_counter()

    answer = None
    evidence = None

    if request.mode == "ai_only":
        answer = local_ai.ask(request.query)

    return QueryResponse(
        ok=True,
        mode=request.mode,
        query=request.query,
        answer=answer,
        evidence=evidence,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
    )
