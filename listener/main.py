import asyncio
import logging
import threading
import uvicorn

from .health import app
from .ws_client import connect_and_listen
from .config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_server():
    logger.info("Starting HTTP server")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level=settings.LOG_LEVEL.lower())


def main():
    logger.info("Launching server thread")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    logger.info("Starting WebSocket listener")
    asyncio.run(connect_and_listen())


if __name__ == "__main__":
    main()
