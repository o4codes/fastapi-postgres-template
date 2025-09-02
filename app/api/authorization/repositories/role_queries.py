"""Role queries."""
from uuid import UUID
from sqlalchemy import select

from app.api.authorization.models import Role
from app.api.users.models import UserRole


def get_user_roles_query(user_id: UUID):
    """
    Get query for user's roles.

    Args:
        user_id: User ID

    Returns:
        SQLAlchemy query for user's roles
    """
    # Get user's roles
    user_roles = (
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )

    return user_roles
