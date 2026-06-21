from __future__ import annotations

import time

from fastapi import APIRouter

from local_ai_search.adapters import local_ai, local_search
from local_ai_search.api.schemas import QueryRequest, QueryResponse
from local_ai_search.artifacts import latest_web_artifact_for_query
from local_ai_search.config import load_config
from local_ai_search.evidence import load_evidence_from_local_search

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

    elif request.mode == "web_only":
        local_search.search(request.query)

        config = load_config()
        artifact_path = latest_web_artifact_for_query(request.query)

        evidence = load_evidence_from_local_search(
            artifact_path,
            limit=request.limit or config.integration.evidence_limit,
            max_chars=request.max_chars or config.integration.evidence_max_chars,
        )

    return QueryResponse(
        ok=True,
        mode=request.mode,
        query=request.query,
        answer=answer,
        evidence=evidence,
        elapsed_ms=int((time.perf_counter() - started) * 1000),
    )