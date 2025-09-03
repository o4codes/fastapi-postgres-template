"""Permission and role-based access control dependencies."""
from typing import Sequence
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authorization.services import RoleService, PermissionService
from app.commons.dependencies.auth import get_current_active_user
from app.configs.db import get_db_session


class PermissionChecker:
    """Permission checker dependency."""

    def __init__(self, permissions: Sequence[str]) -> None:
        """
        Initialize permission checker.

        Args:
            permissions: List of required permission codes
        """
        self.required_permissions = set(permissions)

    async def __call__(
        self,
        current_user=Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db_session),
    ) -> None:
        """
        Check if user has all required permissions.

        Args:
            current_user: Current authenticated user
            db: Database session

        Raises:
            HTTPException: If user lacks required permissions
        """
        service = PermissionService(db)
        user_permissions = await service.get_user_permissions(current_user.id)
        user_permission_codes = {p.code for p in user_permissions}

        if not self.required_permissions.issubset(user_permission_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )


class RoleChecker:
    """Role checker dependency."""

    def __init__(self, roles: Sequence[str]) -> None:
        """
        Initialize role checker.

        Args:
            roles: List of required role codes
        """
        self.required_roles = set(roles)

    async def __call__(
        self,
        current_user=Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db_session),
    ) -> None:
        """
        Check if user has any of the required roles.

        Args:
            current_user: Current authenticated user
            db: Database session

        Raises:
            HTTPException: If user lacks required roles
        """
        service = RoleService(db)
        user_roles = await service.get_user_roles(current_user.id)
        user_role_codes = {r.code for r in user_roles}

        if not self.required_roles.intersection(user_role_codes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Required role not found"
            )


# Type aliases for cleaner dependency injection
def requires_permissions(*permissions: str):
    """
    Dependency for checking required permissions.

    Args:
        *permissions: Required permission codes
    """
    return PermissionChecker(permissions)


def requires_roles(*roles: str):
    """
    Dependency for checking required roles.

    Args:
        *roles: Required role codes
    """
    return RoleChecker(roles)
