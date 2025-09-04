import uuid
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.file_management.models import File
from app.commons.file_storage import S3Storage, GoogleDriveStorage
from app.commons.enums import StorageProvider
from app.commons.errors import AppException
from loguru import logger


class FileService:
    def __init__(
        self, db: AsyncSession, storage_provider: StorageProvider = StorageProvider.S3
    ):
        self.db = db
        self.storage_provider = storage_provider

        # Initialize storage based on provider
        if storage_provider == StorageProvider.S3:
            self.storage = S3Storage(
                bucket_name="your-bucket"
            )  # Configure from settings
        elif storage_provider == StorageProvider.GOOGLE_DRIVE:
            self.storage = GoogleDriveStorage(
                service_account_path="path/to/service-account.json"
            )
        else:
            raise AppException(
                message=f"Unsupported storage provider: {storage_provider}",
                status_code=400,
            )

    async def upload_file(self, file: UploadFile, user_id: str) -> File:
        """Upload file and save metadata."""
        # Generate unique filename
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_filename = (
            f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
        )

        # Upload to storage
        file_content = await file.read()
        await file.seek(0)  # Reset file pointer

        success = await self.storage.upload_file(
            file.file, unique_filename, file.filename, file.content_type
        )
        storage_key = unique_filename

        if not success:
            raise Exception("Failed to upload file to storage")

        # Save metadata to database
        file_record = File(
            user_id=user_id,
            filename=unique_filename,
            original_filename=file.filename,
            content_type=file.content_type,
            size=len(file_content),
            storage_provider=self.storage_provider,
            storage_key=storage_key,
        )

        self.db.add(file_record)
        await self.db.commit()
        await self.db.refresh(file_record)

        return file_record

    async def get_file(self, file_id: str, user_id: str) -> Optional[File]:
        """Get file metadata by ID."""
        result = await self.db.execute(
            select(File).where(File.id == file_id, File.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete file from storage and database."""
        file_record = await self.get_file(file_id, user_id)
        if not file_record:
            return False

        # Delete from storage
        success = await self.storage.delete_file(file_record.storage_key)
        if not success:
            logger.warning(
                f"Failed to delete file from storage: {file_record.storage_key}"
            )

        # Delete from database
        await self.db.delete(file_record)
        await self.db.commit()

        return True

    async def get_download_url(self, file_id: str, user_id: str) -> Optional[str]:
        """Get download URL for file."""
        file_record = await self.get_file(file_id, user_id)
        if not file_record:
            return None

        return await self.storage.get_download_url(file_record.storage_key)
