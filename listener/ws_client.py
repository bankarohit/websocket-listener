import asyncio
import json
import websockets

from .config import settings
from .redis_client import set_status

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
                await ws.send(json.dumps({"token": settings.FYERS_ACCESS_TOKEN}))
                backoff = 1
                async for message in ws:
                    await handle_message(message)
        except Exception as e:
            print(f"WebSocket error: {e}")
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 60)
