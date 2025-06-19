import asyncio
import threading
import uvicorn

from .health import app
from .ws_client import connect_and_listen


def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    asyncio.run(connect_and_listen())


if __name__ == "__main__":
    main()
