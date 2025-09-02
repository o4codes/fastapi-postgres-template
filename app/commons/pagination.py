from typing import Generic, List, TypeVar
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
