import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import asyncio
import json

import pytest

from listener import ws_client, redis_client

class FakeRedis(dict):
    def set(self, key, value):
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

