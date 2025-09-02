from app.commons.schemas import BaseSchema, TimestampSchema, UUIDSchema


class PermissionBase(BaseSchema):
    """Base schema for Permission model."""

    name: str
    code: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    """Schema for creating a new Permission."""

    pass


class PermissionUpdate(PermissionBase):
    """Schema for updating a Permission."""

    name: str | None = None
    code: str | None = None


class PermissionResponse(PermissionBase, UUIDSchema, TimestampSchema):
    """Schema for Permission response."""

    pass
