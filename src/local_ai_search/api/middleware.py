from __future__ import annotations

from fastapi import FastAPI, Request


async def api_request_context(
    request: Request,
    call_next,
):
    response = await call_next(request)
    return response


def register_api_middleware(app: FastAPI) -> None:
    app.middleware("http")(api_request_context)
