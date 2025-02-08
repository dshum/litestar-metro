from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.resolve()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )

    DEBUG: bool = False
    REQUEST_MAX_BODY_SIZE: int = 10_000_000


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        extra="ignore",
    )

    URL: str = "sqlite+aiosqlite:///storage/data/db.sqlite3"
    ECHO: bool = False


class LogSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        env_file=".env",
        extra="ignore",
    )

    LEVEL: str = "ERROR"
    SQLALCHEMY_LEVEL: str = "ERROR"


class ViteSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="VITE_",
        env_file=".env",
        extra="ignore",
    )

    USE_SERVER_LIFETIME: bool = False
    DEV_MODE: bool = False


app = AppSettings()
db = DatabaseSettings()
log = LogSettings()
vite = ViteSettings()
