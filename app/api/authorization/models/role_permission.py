from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.api.authorization.models.permission import Permission
    from app.api.authorization.models.role import Role


class RolePermission(UUIDMixin, TimestampMixin):
    """Association model for role-permission relationships."""

    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    permission_id: Mapped[str] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="role_permissions",
    )
    permission: Mapped["Permission"] = relationship(
        "Permission",
        back_populates="role_permissions",
    )

    def __str__(self) -> str:
        return f"RolePermission(role_id={self.role_id}, permission_id={self.permission_id})"
