"""Two-Factor Authentication schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from app.commons.schemas import UUIDSchema, TimestampSchema


class Enable2FARequest(BaseModel):
    """Enable 2FA request schema."""

    totp_code: str


class Enable2FAResponse(BaseModel):
    """Enable 2FA response schema."""

    secret_key: str
    qr_code: str
    backup_codes: List[str]


class Verify2FARequest(BaseModel):
    """Verify 2FA request schema."""

    totp_code: str


class Disable2FARequest(BaseModel):
    """Disable 2FA request schema."""

    totp_code: str
    password: str


class TwoFactorAuthInfo(UUIDSchema, TimestampSchema):
    """2FA info schema."""

    is_enabled: bool
    remaining_backup_codes: str
    last_used_datetime: Optional[datetime]

    model_config = {"from_attributes": True}
