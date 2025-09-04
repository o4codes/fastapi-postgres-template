from typing import Optional, BinaryIO, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from loguru import logger


class GoogleDriveStorage:
    """Google Drive file storage service."""

    def __init__(self, service_account_path: str, folder_id: Optional[str] = None):
        self.folder_id = folder_id
        credentials = Credentials.from_service_account_file(service_account_path)
        self.service = build("drive", "v3", credentials=credentials)

    async def upload_file(
        self, file: BinaryIO, filename: str, content_type: Optional[str] = None
    ) -> Optional[str]:
        """Upload file to Google Drive."""
        try:
            file_metadata = {"name": filename}
            if self.folder_id:
                file_metadata["parents"] = [self.folder_id]

            media = MediaIoBaseUpload(
                file, mimetype=content_type or "application/octet-stream"
            )

            result = (
                self.service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )

            file_id = result.get("id")
            logger.info(
                f"Successfully uploaded file to Google Drive: {filename} (ID: {file_id})"
            )
            return file_id
        except HttpError as e:
            logger.error(f"Failed to upload file to Google Drive: {e}")
            return None

    async def download_file(self, file_id: str, file_path: str) -> bool:
        """Download file from Google Drive."""
        try:
            request = self.service.files().get_media(fileId=file_id)

            with open(file_path, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

            logger.info(f"Successfully downloaded file from Google Drive: {file_id}")
            return True
        except HttpError as e:
            logger.error(f"Failed to download file from Google Drive: {e}")
            return False

    async def delete_file(self, file_id: str) -> bool:
        """Delete file from Google Drive."""
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Successfully deleted file from Google Drive: {file_id}")
            return True
        except HttpError as e:
            logger.error(f"Failed to delete file from Google Drive: {e}")
            return False

    async def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file information from Google Drive."""
        try:
            result = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id,name,size,mimeType,createdTime,modifiedTime",
                )
                .execute()
            )
            return result
        except HttpError as e:
            logger.error(f"Failed to get file info from Google Drive: {e}")
            return None

    async def file_exists(self, file_id: str) -> bool:
        """Check if file exists in Google Drive."""
        try:
            self.service.files().get(fileId=file_id, fields="id").execute()
            return True
        except HttpError:
            return False

    async def create_public_link(self, file_id: str) -> Optional[str]:
        """Create public sharing link for file."""
        try:
            self.service.permissions().create(
                fileId=file_id, body={"role": "reader", "type": "anyone"}
            ).execute()

            result = (
                self.service.files().get(fileId=file_id, fields="webViewLink").execute()
            )

            return result.get("webViewLink")
        except HttpError as e:
            logger.error(f"Failed to create public link: {e}")
            return None
