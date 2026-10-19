"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Stores configuration required by the API.

    Attributes:
        app_name: Name displayed in the API documentation.
        environment: Current execution environment.
        database_url: PostgreSQL connection string.
        api_key: Secret used to authorize API requests.
    """

    app_name: str = "Yape Monitor API"
    environment: str = "development"
    database_url: str
    api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Returns the cached application settings.

    Returns:
        Settings: Validated application configuration.
    """
    return Settings()
