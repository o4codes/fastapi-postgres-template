"""Response wrapper for standardizing API responses."""
from typing import Any, Callable
from fastapi import Response


def wrap_response(
    message: str = "Success",
    paginated: bool = False,
) -> Callable:
    """
    Dependency to wrap response in standard format.

    Args:
        message: Custom success message
        paginated: If True, don't wrap the response (for paginated endpoints)
    """

    def wrapper(response: Response) -> Callable:
        async def process_response(data: Any) -> dict:
            # Don't wrap paginated responses
            if paginated:
                return data

            return {"status": True, "message": message, "data": data}

        return process_response

    return wrapper
