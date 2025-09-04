from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "app_error"
        self.data = data
        super().__init__(message)
