"""Common schema definitions."""
from typing import TypeVar, Generic
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ResponseWrapper(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    status: bool
    message: str
    data: T

    model_config = ConfigDict(from_attributes=True)
