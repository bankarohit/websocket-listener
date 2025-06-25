import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import asyncio
import json

import pytest

from listener import ws_client, redis_client

class FakeRedis(dict):
    async def set(self, key, value):
        self[key] = value

@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_client, "_redis", fake, raising=False)
    yield fake

@pytest.mark.asyncio
async def test_handle_message_sets_redis(fake_redis):
    message = json.dumps({"id": "123", "status": "filled"})
    await ws_client.handle_message(message)
    assert fake_redis["fyers:123"] == message


@pytest.mark.asyncio
async def test_connect_and_listen_retries(monkeypatch):
    attempts = 0

    class FakeSocket:
        def __init__(self, *args, **kwargs):
            pass

        def subscribe(self, *args, **kwargs):
            pass

        def keep_running(self):
            pass

        def connect(self):
            nonlocal attempts
            attempts += 1
            raise RuntimeError("fail")

    async def fake_sleep(_):
        pass

    monkeypatch.setattr(ws_client, "FyersOrderSocket", FakeSocket)
    monkeypatch.setattr(ws_client.settings, "MAX_RETRIES", 3, raising=False)
    monkeypatch.setattr(ws_client.settings, "RETRY_DELAY", 0, raising=False)
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    with pytest.raises(RuntimeError):
        await ws_client.connect_and_listen()
    assert attempts == 3

