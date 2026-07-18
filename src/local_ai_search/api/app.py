from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from local_ai_search.api.errors import register_api_exception_handlers
from local_ai_search.api.middleware import register_api_middleware
from local_ai_search.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="local_ai_search API", version="0.1")

    register_api_middleware(app)
    register_api_exception_handlers(app)

    app.include_router(router, prefix="/api/v1")

    web_dist = Path(__file__).resolve().parents[1] / "web" / "dist"

    app.mount(
        "/search",
        StaticFiles(directory=web_dist, html=True),
        name="search",
    )

    @app.get("/", include_in_schema=False)
    def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/search/")

    return app
