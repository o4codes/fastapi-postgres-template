from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.api.authorization.models.role import Role
    from app.api.authorization.models.role_permission import RolePermission

class Permission(UUIDMixin, TimestampMixin):
    """Permission model for defining access rights."""
    
    __tablename__ = "permissions"
    
    name: Mapped[str] = mapped_column(
        String(length=100),
        unique=True,
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(
        String(length=100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        String(length=255),
        nullable=True,
    )

    # Relationships
    role_permissions: Mapped[List["RolePermission"]] = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        viewonly=True,
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
