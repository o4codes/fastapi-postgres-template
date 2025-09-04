from enum import Enum


class StorageProvider(str, Enum):
    """Storage provider options."""

    S3 = "s3"
    GOOGLE_DRIVE = "google_drive"
