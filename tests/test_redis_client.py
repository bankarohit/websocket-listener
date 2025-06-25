import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import logging
import pytest

from listener import redis_client

class ErrorRedis:
    async def set(self, key, value):
        raise RuntimeError("boom")

@pytest.mark.asyncio
async def test_set_status_logs_error(monkeypatch, caplog):
    err = ErrorRedis()
    monkeypatch.setattr(redis_client, "_redis", err, raising=False)
    with caplog.at_level(logging.ERROR):
        await redis_client.set_status("k", "v")
    assert "Failed to set key" in caplog.text
