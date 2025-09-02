from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(message)


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
        """Handle application-specific exceptions."""
        response = {
            "message": exc.message,
            "status_code": exc.status_code,
        }
        if exc.data:
            response["data"] = exc.data

        return JSONResponse(
            status_code=exc.status_code,
            content=response,
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": "Validation error",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "data": exc.errors(include_url=False),
            },
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request, exc: IntegrityError
    ) -> JSONResponse:
        """Handle database integrity errors."""
        logger.error(f"Database integrity error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "message": "Database integrity error",
                "status_code": status.HTTP_409_CONFLICT,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle any unhandled exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )
