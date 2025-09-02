"""Permission queries."""
from uuid import UUID
from sqlalchemy import select

from app.api.authorization.models import Permission, RolePermission
from app.api.users.models import UserRole


def get_user_permissions_query(user_id: UUID):
    """
    Get query for user's permissions through their roles.

    Args:
        user_id: User ID

    Returns:
        SQLAlchemy query for user's permissions
    """
    # Get permissions through user roles
    role_permissions = (
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user_id)
    )

    return role_permissions
