from typing import List
from uuid import UUID

from app.commons.schemas import BaseSchema, TimestampSchema, UUIDSchema
from app.api.authorization.schema.permission import PermissionResponse

class RoleBase(BaseSchema):
    """Base schema for Role model."""
    name: str
    description: str | None = None
    is_default: bool = False
    is_system: bool = False

class RoleCreate(RoleBase):
    """Schema for creating a new Role."""
    permission_ids: List[UUID] | None = None

class RoleUpdate(RoleBase):
    """Schema for updating a Role."""
    name: str | None = None
    permission_ids: List[UUID] | None = None

class RoleResponse(RoleBase, UUIDSchema, TimestampSchema):
    """Schema for Role response."""
    permissions: List[PermissionResponse]
