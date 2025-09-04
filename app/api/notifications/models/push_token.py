from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.commons.models import TimestampMixin, UUIDMixin


class PushToken(UUIDMixin, TimestampMixin):
    """Push notification token model."""

    __tablename__ = "push_tokens"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    platform: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # ios, android, web

    def __str__(self) -> str:
        return f"{self.platform} - {self.user_id}"
