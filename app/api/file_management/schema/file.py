from datetime import datetime
from pydantic import BaseModel
from app.commons.enums import StorageProvider


class FileResponse(BaseModel):
    id: str
    user_id: str
    filename: str
    original_filename: str
    content_type: str
    size: int
    storage_provider: StorageProvider
    created_datetime: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    download_url: str
