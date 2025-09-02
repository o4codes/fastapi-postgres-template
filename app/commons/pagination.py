import base64
import json
from typing import Any, Dict, Generic, List, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    page: int = 1
    page_size: int = 10

    model_config = ConfigDict(from_attributes=True)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageInfo(BaseModel):
    """Pagination metadata."""

    total: int
    page: int
    page_size: int
    pages: int
    has_next: bool
    has_previous: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    page_info: PageInfo

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        params: PaginationParams,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        pages = (total + params.page_size - 1) // params.page_size

        page_info = PageInfo(
            total=total,
            page=params.page,
            page_size=params.page_size,
            pages=pages,
            has_next=params.page < pages,
            has_previous=params.page > 1,
        )

        return cls(
            items=items,
            page_info=page_info,
        )


class CursorPagination:
    """Helper class for cursor-based pagination."""

    @staticmethod
    def encode_cursor(data: Dict[str, Any]) -> str:
        """Encode cursor data to base64."""
        json_str = json.dumps(data)
        bytes_str = json_str.encode("utf-8")
        base64_str = base64.urlsafe_b64encode(bytes_str).decode("utf-8")
        return base64_str

    @staticmethod
    def decode_cursor(cursor: str) -> Dict[str, Any]:
        """Decode cursor from base64."""
        try:
            bytes_str = base64.urlsafe_b64decode(cursor.encode("utf-8"))
            json_str = bytes_str.decode("utf-8")
            return json.loads(json_str)
        except (ValueError, json.JSONDecodeError):
            raise ValueError("Invalid cursor format")


class CursorPaginationParams(BaseModel):
    """Parameters for cursor-based pagination."""

    cursor: str | None = None
    limit: int = 10
    order_by: str | None = None
    direction: str = "forward"

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "cursor": "eyJpZCI6IjEyMzQ1Njc4LTEyMzQtNTY3OC0xMjM0LTU2NzgxMjM0NTY3OCJ9",
                "limit": 10,
                "order_by": "created_datetime",
                "direction": "forward",
            }
        },
    )


class CursorPageInfo(BaseModel):
    """Cursor pagination metadata."""

    next_cursor: str | None
    previous_cursor: str | None
    has_next: bool
    has_previous: bool

    model_config = ConfigDict(from_attributes=True)


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Generic cursor-paginated response."""

    page_info: CursorPageInfo
    items: List[T]

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(
        cls,
        items: List[T],
        has_next: bool,
        has_previous: bool,
        next_cursor: str | None = None,
        previous_cursor: str | None = None,
    ) -> "CursorPaginatedResponse[T]":
        """Create a cursor-paginated response."""
        page_info = CursorPageInfo(
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
            has_next=has_next,
            has_previous=has_previous,
        )

        return cls(
            items=items,
            page_info=page_info,
        )
