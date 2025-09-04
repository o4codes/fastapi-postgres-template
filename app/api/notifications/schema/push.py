from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PushTokenCreate(BaseModel):
    token: str
    platform: str  # ios, android, web


class PushTokenResponse(BaseModel):
    id: str
    user_id: str
    token: str
    platform: str
    created_datetime: datetime

    class Config:
        from_attributes = True


class PushNotificationSend(BaseModel):
    title: str
    message: str
    user_ids: Optional[list[str]] = None  # If None, send to all users
    data: Optional[dict] = None
