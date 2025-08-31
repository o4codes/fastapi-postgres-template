from uuid import UUID

from app.commons.schemas import BaseSchema, TimestampSchema, UUIDSchema
from app.api.authorization.schema.permission import PermissionResponse
from app.api.authorization.schema.role import RoleResponse

class RolePermissionBase(BaseSchema):
    """Base schema for RolePermission model."""
    role_id: UUID
    permission_id: UUID

class RolePermissionCreate(RolePermissionBase):
    """Schema for creating a new RolePermission."""
    pass

class RolePermissionUpdate(RolePermissionBase):
    """Schema for updating a RolePermission."""
    role_id: UUID | None = None
    permission_id: UUID | None = None

class RolePermissionResponse(RolePermissionBase, UUIDSchema, TimestampSchema):
    """Schema for RolePermission response."""
    role: RoleResponse | None = None
    permission: PermissionResponse | None = None
