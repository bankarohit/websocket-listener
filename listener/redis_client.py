import redis.asyncio as redis
from .config import settings

_redis = None

def get_client() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL)
    return _redis

async def set_status(key: str, value: str) -> None:
    client = get_client()
    await client.set(key, value)
