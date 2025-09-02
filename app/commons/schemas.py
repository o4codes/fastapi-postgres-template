from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configurations."""

    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM model parsing
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid),
        },
    )


class TimestampSchema(BaseSchema):
    """Schema mixin for timestamp fields."""

    created_datetime: datetime
    updated_datetime: datetime


class UUIDSchema(BaseSchema):
    """Schema mixin for UUID primary key."""

    id: UUID


class SoftDeleteSchema(BaseSchema):
    """Schema mixin for soft delete field."""

    deleted_datetime: Optional[datetime] = None


class AuditSchema(BaseSchema):
    """Schema mixin for audit fields."""

    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
