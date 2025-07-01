import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import asyncio

from listener import main as main_mod


def test_run_server_invokes_uvicorn(monkeypatch):
    called = {}

    def fake_run(app, host=None, port=None, log_level=None):
        called['app'] = app
        called['host'] = host
        called['port'] = port
        called['log_level'] = log_level

    monkeypatch.setattr(main_mod.uvicorn, "run", fake_run)

    main_mod.run_server()

    assert called['app'] is main_mod.app
    assert called['host'] == "0.0.0.0"
    assert called['port'] == 8000
    assert called['log_level'] == main_mod.settings.LOG_LEVEL.lower()


def test_main_starts_thread_and_runs_listener(monkeypatch):
    events = {"connect_called": False, "thread_started": False}

    def fake_uvicorn_run(*args, **kwargs):
        events['uvicorn_called'] = True

    monkeypatch.setattr(main_mod.uvicorn, "run", fake_uvicorn_run)

    async def fake_connect_and_listen():
        events["connect_called"] = True

    monkeypatch.setattr(main_mod, "connect_and_listen", fake_connect_and_listen)

    class FakeThread:
        def __init__(self, target=None, daemon=None):
            self.target = target
            self.daemon = daemon

        def start(self):
            events["thread_started"] = True
            if self.target:
                self.target()

    monkeypatch.setattr(main_mod.threading, "Thread", FakeThread)

    def fake_asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(main_mod.asyncio, "run", fake_asyncio_run)

    main_mod.main()

    assert events["thread_started"] is True
    assert events["connect_called"] is True


def test_main_exchanges_auth_code(monkeypatch):
    events = {}

    monkeypatch.setattr(main_mod.uvicorn, "run", lambda *a, **k: None)

    async def fake_exchange(code):
        events["code"] = code
        return "TOKEN123", "REFRESH123"

    monkeypatch.setattr(main_mod.auth, "exchange_auth_code", fake_exchange)

    async def fake_connect_and_listen():
        events["token"] = main_mod.settings.FYERS_ACCESS_TOKEN
        events["refresh"] = main_mod.settings.FYERS_REFRESH_TOKEN

    monkeypatch.setattr(main_mod, "connect_and_listen", fake_connect_and_listen)

    class FakeThread:
        def __init__(self, target=None, daemon=None):
            self.target = target

        def start(self):
            if self.target:
                self.target()

    monkeypatch.setattr(main_mod.threading, "Thread", FakeThread)

    monkeypatch.setattr(main_mod.settings, "FYERS_ACCESS_TOKEN", "", raising=False)
    monkeypatch.setattr(main_mod.settings, "FYERS_REFRESH_TOKEN", "", raising=False)
    monkeypatch.setattr(main_mod.settings, "FYERS_AUTH_CODE", "CODE", raising=False)

    def fake_asyncio_run(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    monkeypatch.setattr(main_mod.asyncio, "run", fake_asyncio_run)

    main_mod.main()

    assert events["code"] == "CODE"
    assert events["token"] == "TOKEN123"
    assert events["refresh"] == "REFRESH123"
