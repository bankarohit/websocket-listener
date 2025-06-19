import redis
from .config import settings

_redis = None

def get_client() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL)
    return _redis

def set_status(key: str, value: str) -> None:
    client = get_client()
    client.set(key, value)
