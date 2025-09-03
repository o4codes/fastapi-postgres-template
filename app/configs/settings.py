from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
    )

    project_name: str = Field(
        default="FastAPI Postgres Template",
        description="Project name",
    )
    version: str = Field(
        default="1.0.0",
        description="Project version",
    )
    description: str = Field(
        default="FastAPI Postgres Template",
        description="Project description",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    jwt_secret_key: str
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT token algorithm",
    )

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    # Redis settings
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default=None)

    # Email settings
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: str
    smtp_password: str
    smtp_from_email: str
    smtp_from_name: str = Field(default="FastAPI App")
    smtp_tls: bool = Field(default=True)
    smtp_ssl: bool = Field(default=False)


# Create a single instance of Settings
_settings = Settings()


def get_settings() -> Settings:
    """
    Returns the settings instance.

    Returns:
        Settings: The application settings instance
    """
    return _settings
