from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiException(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        error_type: str,
        message: str,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.message = message


def _error_response(
    *,
    status_code: int,
    error_type: str,
    message: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": {
                "type": error_type,
                "message": message,
            },
        },
    )


async def api_exception_handler(
    request: Request,
    exc: ApiException,
) -> JSONResponse:
    return _error_response(
        status_code=exc.status_code,
        error_type=exc.error_type,
        message=exc.message,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return _error_response(
        status_code=422,
        error_type="validation_error",
        message="The request is invalid.",
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."

    return _error_response(
        status_code=exc.status_code,
        error_type="not_found" if exc.status_code == 404 else "http_error",
        message=message,
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return _error_response(
        status_code=500,
        error_type="internal_error",
        message="The request could not be completed.",
    )


def register_api_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiException, api_exception_handler)
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,
    )
    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )
