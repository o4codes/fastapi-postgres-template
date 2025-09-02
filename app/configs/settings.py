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

    @property
    def SECRET_KEY(self) -> str:
        return self.jwt_secret_key

    @property
    def ALGORITHM(self) -> str:
        return self.jwt_algorithm

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    # Redis settings
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default=None)


# Create a single instance of Settings
_settings = Settings()


def get_settings() -> Settings:
    """
    Returns the settings instance.

    Returns:
        Settings: The application settings instance
    """
    return _settings
