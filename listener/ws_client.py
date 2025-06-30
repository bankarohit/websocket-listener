import asyncio
import json
import logging
from typing import Any, Dict

from fyers_apiv3.FyersWebsocket.order_ws import FyersOrderSocket

from .config import settings
from .redis_client import set_status
from . import auth

logger = logging.getLogger(__name__)

async def handle_message(message: Any) -> None:
    """Store a received WebSocket message in Redis."""
    if isinstance(message, str):
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            data = {"raw": message}
    else:
        data = message
    logger.debug("Received message: %s", data)

    key = (
        data.get("id")
        or data.get("orders", {}).get("id")
        or "last"
    )
    await set_status(f"fyers:{key}", json.dumps(data))

async def connect_and_listen() -> None:
    """Connect to the Fyers WebSocket and process updates indefinitely."""
    loop = asyncio.get_running_loop()

    def dispatch(msg: Dict[str, Any]):
        asyncio.run_coroutine_threadsafe(handle_message(msg), loop)

    def on_connect() -> None:
        logger.info("Connected to WebSocket")
        socket.subscribe(settings.FYERS_SUBSCRIPTION_TYPE)
        socket.keep_running()

    def on_close(message: Dict[str, Any]) -> None:
        logger.warning("WebSocket closed: %s", message)

    def on_error(message: Dict[str, Any]) -> None:
        logger.error("WebSocket error: %s", message)

    socket = FyersOrderSocket(
        access_token=settings.FYERS_ACCESS_TOKEN,
        on_connect=on_connect,
        on_close=on_close,
        on_error=on_error,
        on_general=dispatch,
        on_orders=dispatch,
        on_positions=dispatch,
        on_trades=dispatch,
    )

    attempt = 0
    while True:
        try:
            logger.info("Connecting to Fyers WebSocket")
            socket.connect()
            attempt = 0
            while True:
                await asyncio.sleep(1)
        except Exception as exc:
            msg = str(exc).lower()
            if (
                settings.FYERS_REFRESH_TOKEN
                and "token" in msg
                and ("expired" in msg or "unauth" in msg or "invalid" in msg)
            ):
                try:
                    logger.info("Refreshing access token")
                    new = await auth.refresh_access_token(
                        settings.FYERS_REFRESH_TOKEN,
                        settings.FYERS_PIN,
                    )
                    if new:
                        settings.FYERS_ACCESS_TOKEN = new
                        socket = FyersOrderSocket(
                            access_token=new,
                            on_connect=on_connect,
                            on_close=on_close,
                            on_error=on_error,
                            on_general=dispatch,
                            on_orders=dispatch,
                            on_positions=dispatch,
                            on_trades=dispatch,
                        )
                        continue
                except Exception:
                    logger.exception("Token refresh failed")

            attempt += 1
            logger.exception("Connection attempt %s failed", attempt)
            if attempt >= settings.MAX_RETRIES:
                raise
            delay = settings.RETRY_DELAY * 2 ** (attempt - 1)
            await asyncio.sleep(delay)
