import logging
import uuid

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.client_ip import get_client_ip
from app.middleware.log import setup_logger

logger = setup_logger(__name__)

# Only the status codes this scaffold's code actually raises (security.py: 401;
# FastAPI/Pydantic request validation: 422) plus the generic-handler's own 500.
# Anything else falls back to "api_error" below — add entries here as routes
# start raising their own HTTPException status codes.
HTTP_STATUS_ERROR_CODES: dict[int, str] = {
    401: "unauthorized",
    422: "validation_error",
    500: "internal_error",
}

GENERIC_INTERNAL_ERROR_MESSAGE = "An unexpected error occurred."


def error_response_body(*, message: str, error_code: str) -> dict:
    return {
        "success": False,
        "details": {
            "message": message,
            "error_code": error_code,
        },
        "data": None,
    }


def error_code_for_http_exception(exc: HTTPException) -> str:
    return HTTP_STATUS_ERROR_CODES.get(exc.status_code, "api_error")


def message_for_http_exception(exc: HTTPException) -> str:
    detail = exc.detail
    if isinstance(detail, str):
        return detail
    if detail is None:
        return "Invalid request."
    return str(detail)


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", str(uuid.uuid4()))


def _response_headers(request: Request) -> dict[str, str]:
    return {"X-Request-ID": _request_id(request)}


async def handle_generic_exception(request: Request, exc: Exception):
    request_id = _request_id(request)
    error_data = {
        "log_type": "generic_exception",
        "error_message": str(exc),
        "status_code": 500,
        "request_id": request_id,
    }
    logger.error(
        "Generic exception occurred", extra={"data": error_data}, exc_info=True
    )
    return JSONResponse(
        content=error_response_body(
            message=GENERIC_INTERNAL_ERROR_MESSAGE,
            error_code="internal_error",
        ),
        status_code=500,
        headers=_response_headers(request),
    )


async def handle_http_exception(request: Request, exc: HTTPException):
    request_id = _request_id(request)
    error_code = error_code_for_http_exception(exc)
    error_data = {
        "log_type": "http_exception",
        "error_message": exc.detail,
        "status_code": exc.status_code,
        "request_id": request_id,
        "path": request.url.path,
        "client_ip": get_client_ip(request),
        "user_agent": request.headers.get("User-Agent"),
        "error_code": error_code,
    }
    level = logging.WARNING if exc.status_code >= 500 else logging.INFO
    logger.log(level, "HTTP exception occurred", extra={"data": error_data})

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response_body(
            message=message_for_http_exception(exc),
            error_code=error_code,
        ),
        headers=_response_headers(request),
    )
