"""Response wrapper dependencies."""
from typing import TypeVar, Callable, Any

from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response

from app.commons.schemas import ResponseWrapper

T = TypeVar("T")


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


class ResponseWrapperRoute(APIRoute):
    """Route that wraps all responses in a ResponseWrapper."""

    def get_route_handler(self) -> Callable:
        """Get route handler."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            """Custom route handler that wraps response in ResponseWrapper."""
            response: Any = await original_route_handler(request)

            # Don't wrap responses that are already wrapped
            if isinstance(response, ResponseWrapper):
                return response

            # Don't wrap Response objects (FileResponse, StreamingResponse, etc.)
            if isinstance(response, Response):
                return response

            return ResponseWrapper(data=response)

        return custom_route_handler
