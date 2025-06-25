import asyncio
import json
import logging
import websockets

from .config import settings
from .redis_client import set_status

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

async def handle_message(message: str) -> None:
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        data = {"raw": message}
    key = data.get("id", "last")
    set_status(f"fyers:{key}", json.dumps(data))

async def connect_and_listen():
    backoff = 1
    while True:
        try:
            async with websockets.connect(settings.FYERS_WEBSOCKET_URL) as ws:
                logger.info("Connected to WebSocket")
                await ws.send(json.dumps({"token": settings.FYERS_ACCESS_TOKEN}))
                backoff = 1
                async for message in ws:
                    await handle_message(message)
        except Exception as e:
            logger.error("WebSocket error: %s", e)
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 60)
