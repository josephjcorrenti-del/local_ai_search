from __future__ import annotations

from fastapi import FastAPI

from local_ai_search.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="local_ai_search API", version="0.1")
    app.include_router(router, prefix="/api/v1")
    return app
