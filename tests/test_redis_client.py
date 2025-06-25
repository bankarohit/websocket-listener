import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import logging
import pytest

from listener import redis_client

class ErrorRedis:
    async def set(self, key, value):
        raise RuntimeError("boom")


class FakeRedis(dict):
    """Simple Redis stand-in with ping and set methods."""

    def __init__(self):
        super().__init__()
        self.pings = 0

    async def ping(self):
        self.pings += 1

    async def set(self, key, value):
        self[key] = value

@pytest.mark.asyncio
async def test_set_status_logs_error(monkeypatch, caplog):
    err = ErrorRedis()
    monkeypatch.setattr(redis_client, "_redis", err, raising=False)
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            await redis_client.set_status("k", "v")
    assert "Failed to set key" in caplog.text


@pytest.mark.asyncio
async def test_get_client_initializes(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_client, "_redis", None, raising=False)
    monkeypatch.setattr(redis_client.redis, "from_url", lambda *a, **k: fake)

    client = await redis_client.get_client(timeout=0.1)

    assert client is fake
    assert fake.pings == 1
    assert redis_client._redis is fake


@pytest.mark.asyncio
async def test_get_client_ping_error(monkeypatch, caplog):
    class BadRedis(FakeRedis):
        async def ping(self):
            raise RuntimeError("fail")

    bad = BadRedis()
    monkeypatch.setattr(redis_client, "_redis", None, raising=False)
    monkeypatch.setattr(redis_client.redis, "from_url", lambda *a, **k: bad)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError):
            await redis_client.get_client()

    assert "Redis connection failed" in caplog.text


@pytest.mark.asyncio
async def test_set_status_stores_value(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_client, "_redis", fake, raising=False)

    await redis_client.set_status("foo", "bar")

    assert fake["foo"] == "bar"
