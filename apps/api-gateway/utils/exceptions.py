"""
Custom exceptions and error handlers.
"""

import os
from datetime import datetime, timezone

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


def _cors_json_response(status_code: int, content: dict, request: Request | None = None) -> JSONResponse:
    """
    Build a JSONResponse and always inject CORS headers.

    Belt-and-suspenders: Starlette's error pathway can bypass CORSMiddleware
    in certain scenarios (e.g. 500s raised before the middleware chain
    completes). Injecting Access-Control-Allow-Origin here guarantees the
    browser always receives a readable error body instead of a CORS failure.
    """
    # Determine allowed origin from the request or fall back to wildcard
    origin = "*"
    if request is not None:
        origin = request.headers.get("origin", "*")

    # Read configured origins; only reflect the request origin if it is allowed
    configured = os.getenv("CORS_ORIGINS", '["http://localhost:3000"]')
    try:
        import json as _json
        allowed = _json.loads(configured)
    except Exception:
        allowed = ["http://localhost:3000"]

    if origin not in allowed and "*" not in allowed:
        origin = allowed[0] if allowed else "*"

    resp = JSONResponse(status_code=status_code, content=content)
    resp.headers["Access-Control-Allow-Origin"] = origin
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    return resp


class CyberShieldException(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "internal_error"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(CyberShieldException):
    """Input validation error."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400, error_code="validation_error")


class AuthenticationError(CyberShieldException):
    """Authentication failure."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="authentication_error")


class NotFoundError(CyberShieldException):
    """Resource not found."""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=404, error_code="not_found")


def setup_exception_handlers(app):
    """Register all exception handlers with FastAPI app."""

    @app.exception_handler(CyberShieldException)
    async def handle_cybershield_exception(request: Request, exc: CyberShieldException):
        return _cors_json_response(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "path": str(request.url),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

        return _cors_json_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "Request validation failed",
                "details": errors,
                "path": str(request.url),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError):
        return _cors_json_response(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "conflict",
                "message": "Resource already exists or constraint violated",
                "path": str(request.url),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception):
        import traceback
        print(f"Unhandled exception: {exc}")
        traceback.print_exc()
        try:
            with open(r"e:\cybershield-ai\tmp_crash.log", "w") as f:
                f.write(f"Unhandled exception: {exc}\n")
                f.write(traceback.format_exc())
        except Exception:
            pass

        return _cors_json_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "path": str(request.url),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            request=request,
        )