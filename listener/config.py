"""Application configuration handled via Pydantic settings."""

try:  # Pydantic <2.5
    from pydantic import BaseSettings
except Exception:  # pragma: no cover - fall back for Pydantic >=2.0
    from pydantic_settings import BaseSettings  # type: ignore


class Settings(BaseSettings):
    """Validate and expose environment configuration."""

    FYERS_APP_ID: str = ""
    FYERS_ACCESS_TOKEN: str = ""
    FYERS_SUBSCRIPTION_TYPE: str = "OnOrders"

    REDIS_URL: str = "redis://localhost:6379/0"
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 5
    RETRY_DELAY: float = 1.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
