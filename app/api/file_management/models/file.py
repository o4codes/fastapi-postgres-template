from sqlalchemy import String, Integer, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.commons.models import TimestampMixin, UUIDMixin
from app.commons.enums import StorageProvider


class File(UUIDMixin, TimestampMixin):
    """File model for tracking uploaded files."""

    __tablename__ = "files"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_provider: Mapped[StorageProvider] = mapped_column(
        Enum(StorageProvider), nullable=False
    )
    storage_key: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # file ID or path

    def __str__(self) -> str:
        return f"{self.original_filename} - {self.user_id}"
