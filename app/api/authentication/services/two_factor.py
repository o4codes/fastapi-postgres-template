"""Two-Factor Authentication service."""
import pyotp
import qrcode
import json
from io import BytesIO
import base64
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.authentication import models as auth_models
from app.api.authentication.schema import two_factor as two_factor_schema
from app.api.authentication.services.auth import AuthService
from app.api.users import models as user_models


class TwoFactorAuthService:
    """Service for 2FA operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_totp_secret() -> str:
        """Generate random secret for TOTP."""
        return pyotp.random_base32()

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes."""
        return [pyotp.random_base32(length=8) for _ in range(count)]

    @staticmethod
    def verify_totp(secret_key: str, totp_code: str) -> bool:
        """Verify TOTP code."""
        totp = pyotp.TOTP(secret_key)
        return totp.verify(totp_code)

    def generate_qr_code(self, secret_key: str, email: str) -> str:
        """Generate QR code for 2FA setup."""
        # Create TOTP URI (otpauth://totp/App:user@email.com?secret=KEY&issuer=App)
        totp = pyotp.TOTP(secret_key)
        provisioning_uri = totp.provisioning_uri(email, issuer_name="FastAPI App")

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Create image and convert to base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered)
        img_str = base64.b64encode(buffered.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    async def setup_2fa(self, user_id: UUID) -> two_factor_schema.Enable2FAResponse:
        """Set up 2FA for user."""
        # Generate secret key and backup codes
        secret_key = self.generate_totp_secret()
        backup_codes = self.generate_backup_codes()

        # Get user's email for QR code
        query = select(user_models.User).where(user_models.User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one()

        # Generate QR code
        qr_code = self.generate_qr_code(secret_key, user.email)

        # Create or update 2FA record
        query = select(auth_models.TwoFactorAuth).where(
            auth_models.TwoFactorAuth.user_id == user_id
        )
        result = await self.db.execute(query)
        two_factor = result.scalar_one_or_none()

        if two_factor:
            two_factor.secret_key = secret_key
            two_factor.backup_codes = json.dumps(backup_codes)
            two_factor.is_enabled = False
        else:
            two_factor = auth_models.TwoFactorAuth(
                user_id=user_id,
                secret_key=secret_key,
                backup_codes=json.dumps(backup_codes),
                is_enabled=False,
            )
            self.db.add(two_factor)

        await self.db.commit()

        return two_factor_schema.Enable2FAResponse(
            secret_key=secret_key,
            qr_code=qr_code,
            backup_codes=backup_codes,
        )

    async def enable_2fa(self, user_id: UUID, totp_code: str) -> None:
        """Enable 2FA for user."""
        # Get 2FA record
        query = select(auth_models.TwoFactorAuth).where(
            auth_models.TwoFactorAuth.user_id == user_id
        )
        result = await self.db.execute(query)
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA not set up",
            )

        # Verify TOTP code
        if not self.verify_totp(two_factor.secret_key, totp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code",
            )

        # Enable 2FA
        two_factor.is_enabled = True
        two_factor.last_used_datetime = datetime.now(tz=timezone.utc)
        await self.db.commit()

    async def disable_2fa(self, user_id: UUID, password: str, totp_code: str) -> None:
        """Disable 2FA for user."""
        # Get 2FA record
        query = select(auth_models.TwoFactorAuth).where(
            auth_models.TwoFactorAuth.user_id == user_id
        )
        result = await self.db.execute(query)
        two_factor = result.scalar_one_or_none()

        if not two_factor or not two_factor.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA not enabled",
            )

        # Get user to verify password
        query = select(user_models.User).where(user_models.User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one()

        # Verify password
        auth_service = AuthService(self.db)
        if not auth_service.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password",
            )

        # Verify TOTP code
        if not self.verify_totp(two_factor.secret_key, totp_code):
            # Check backup codes
            backup_codes = json.loads(two_factor.backup_codes)
            if totp_code not in backup_codes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid TOTP code",
                )
            # Remove used backup code
            backup_codes.remove(totp_code)
            two_factor.backup_codes = json.dumps(backup_codes)

        # Disable 2FA
        two_factor.is_enabled = False
        two_factor.last_used_at = datetime.now(tz=timezone.utc)
        await self.db.commit()

    async def get_2fa_info(self, user_id: UUID) -> auth_models.TwoFactorAuth:
        """Get 2FA status for user."""
        query = select(auth_models.TwoFactorAuth).where(
            auth_models.TwoFactorAuth.user_id == user_id
        )
        result = await self.db.execute(query)
        two_factor = result.scalar_one_or_none()

        if not two_factor:
            return auth_models.TwoFactorAuth(
                is_enabled=False,
                created_at=datetime.now(tz=timezone.utc),
                last_used_datetime=None,
                remaining_backup_codes=0,
            )

        backup_codes = json.loads(two_factor.backup_codes)
        return auth_models.TwoFactorAuth(
            is_enabled=two_factor.is_enabled,
            created_datetime=two_factor.created_datetime,
            last_used_datetime=two_factor.last_used_datetime,
            remaining_backup_codes=len(backup_codes),
        )
