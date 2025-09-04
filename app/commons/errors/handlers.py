import time
from typing import Any, Dict

from fastapi import Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from .exception import AppException


def create_error_response(
    request: Request, message: str, error_code: str = None, data: Any = None
) -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "status": False,
        "path": request.url.path,
        "timestamp": int(time.time() * 1000),
        "error_code": error_code,
        "message": message,
        "data": data,
    }


async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            request=request,
            message=exc.message,
            status_code=exc.status_code,
            error_code=exc.error_code,
            data=exc.data,
        ),
    )


async def handle_validation_error(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            request=request,
            message="Invalid submitted data",
            error_code="validation_error",
            data=exc.errors(include_url=False),
        ),
    )


async def handle_request_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            request=request,
            message="Invalid submitted data",
            error_code="validation_error",
            data=exc.errors(),
        ),
    )


async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors."""
    logger.error(f"Database integrity error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=create_error_response(
            request=request,
            message="Data integrity error",
            error_code="integrity_error",
        ),
    )


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            request=request, message=exc.detail, error_code=None
        ),
    )


async def handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            request=request,
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="internal_server_error",
        ),
    )


EXCEPTION_HANDLERS_MAPPING = {
    AppException: handle_app_exception,
    ValidationError: handle_validation_error,
    RequestValidationError: handle_request_validation_error,
    IntegrityError: handle_integrity_error,
    HTTPException: handle_http_exception,
    Exception: handle_unhandled_exception,
}
