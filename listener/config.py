import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    FYERS_APP_ID: str = os.getenv("FYERS_APP_ID", "")
    FYERS_ACCESS_TOKEN: str = os.getenv("FYERS_ACCESS_TOKEN", "")
    FYERS_WEBSOCKET_URL: str = os.getenv("FYERS_WEBSOCKET_URL", "wss://example.com/ws")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
