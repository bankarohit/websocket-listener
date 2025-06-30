"""Application configuration handled via Pydantic settings."""

try:  # Pydantic <2.5
    from pydantic import BaseSettings, Field
except ImportError:  # pragma: no cover - fall back for Pydantic >=2.0
    from pydantic_settings import BaseSettings  # type: ignore
    from pydantic import Field


class Settings(BaseSettings):
    """Validate and expose environment configuration."""

    FYERS_APP_ID: str = Field("", env="FYERS_APP_ID")
    FYERS_SECRET_KEY: str = Field("", env="FYERS_SECRET_KEY")
    FYERS_REDIRECT_URI: str = Field("", env="FYERS_REDIRECT_URI")
    FYERS_ACCESS_TOKEN: str = Field("", env="FYERS_ACCESS_TOKEN")
    FYERS_AUTH_CODE: str = Field("", env="FYERS_AUTH_CODE")
    FYERS_REFRESH_TOKEN: str = Field("", env="FYERS_REFRESH_TOKEN")
    FYERS_PIN: str = Field("", env="FYERS_PIN")
    FYERS_SUBSCRIPTION_TYPE: str = Field("OnOrders", env="FYERS_SUBSCRIPTION_TYPE")

    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    MAX_RETRIES: int = Field(5, env="MAX_RETRIES")
    RETRY_DELAY: float = Field(1.0, env="RETRY_DELAY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
