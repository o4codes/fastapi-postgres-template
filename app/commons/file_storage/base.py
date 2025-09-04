from abc import ABC, abstractmethod
from typing import Optional, BinaryIO


class BaseFileStorage(ABC):
    """Abstract base class for file storage implementations."""

    @abstractmethod
    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        filename: str,
        content_type: Optional[str] = None,
    ) -> bool:
        """Upload file to storage."""
        pass

    @abstractmethod
    async def download_file(self, key: str, file_path: str) -> bool:
        """Download file from storage."""
        pass

    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """Delete file from storage."""
        pass

    @abstractmethod
    async def file_exists(self, key: str) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    async def get_download_url(self, key: str) -> Optional[str]:
        """Get download URL for file."""
        pass
