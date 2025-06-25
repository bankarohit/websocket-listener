import logging
import redis.asyncio as redis
from .config import settings

logger = logging.getLogger(__name__)

_redis = None

async def get_client(timeout: float | None = None) -> redis.Redis:
    global _redis
    if _redis is None:
        logger.info("Connecting to Redis at %s", settings.REDIS_URL)
        _redis = redis.from_url(settings.REDIS_URL, socket_timeout=timeout)
        try:
            await _redis.ping()
        except Exception:
            logger.exception("Redis connection failed")
            raise
    return _redis

async def set_status(key: str, value: str, timeout: float | None = None) -> None:
    client = await get_client(timeout)
    try:
        await client.set(key, value)
    except Exception:
        logger.exception("Failed to set key %s", key)
        raise
