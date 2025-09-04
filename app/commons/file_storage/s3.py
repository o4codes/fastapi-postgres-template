import aioboto3
from typing import Optional, BinaryIO
from botocore.exceptions import ClientError
from loguru import logger
from .base import BaseFileStorage


class S3Storage(BaseFileStorage):
    """AWS S3 file storage service."""

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: str = "us-east-1",
    ):
        self.bucket_name = bucket_name
        self.session = aioboto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    async def upload_file(
        self,
        file: BinaryIO,
        key: str,
        filename: str,
        content_type: Optional[str] = None,
    ) -> bool:
        """Upload file to S3."""
        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            async with self.session.client("s3") as s3:
                await s3.upload_fileobj(
                    file, self.bucket_name, key, ExtraArgs=extra_args
                )
            logger.info(f"Successfully uploaded file to S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return False

    async def download_file(self, key: str, file_path: str) -> bool:
        """Download file from S3."""
        try:
            async with self.session.client("s3") as s3:
                await s3.download_file(self.bucket_name, key, file_path)
            logger.info(f"Successfully downloaded file from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {e}")
            return False

    async def delete_file(self, key: str) -> bool:
        """Delete file from S3."""
        try:
            async with self.session.client("s3") as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Successfully deleted file from S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False

    async def get_download_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """Generate presigned URL for file access."""
        try:
            async with self.session.client("s3") as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expiration,
                )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    async def file_exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        try:
            async with self.session.client("s3") as s3:
                await s3.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
