from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    clerk_secret_key: str
    clerk_issuer: str
    clerk_authorized_parties: list[str]
    clerk_audience: str | None = None
    openrouter_api_key: str
    openrouter_model: str
    openrouter_timeout_ms: int = Field(default=25_000, gt=0)
    cors_origins: list[str]

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )