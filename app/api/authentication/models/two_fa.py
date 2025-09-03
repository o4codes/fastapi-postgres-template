"""Authentication models."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.commons.models import UUIDMixin, TimestampMixin


class TwoFactorAuth(UUIDMixin, TimestampMixin):
    """Two Factor Authentication model."""

    __tablename__ = "two_factor_auth"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    secret_key: Mapped[str] = mapped_column(String(32))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    backup_codes: Mapped[str] = mapped_column(
        String(512)
    )  # JSON string of unused backup codes
    last_used_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="two_factor_auth")
