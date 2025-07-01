import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import asyncio
import pytest

from listener import auth


class FakeSession:
    def __init__(self, *args, **kwargs):
        self.token = None

    def set_token(self, token):
        self.token = token

    def generate_authcode(self):
        return "url"

    def generate_token(self):
        return {"access_token": "TOKEN", "refresh_token": "REF"}


@pytest.mark.asyncio
async def test_exchange_auth_code(monkeypatch):
    monkeypatch.setattr(auth.fyersModel, "SessionModel", lambda *a, **k: FakeSession())

    access, refresh = await auth.exchange_auth_code("code")

    assert access == "TOKEN"
    assert refresh == "REF"


def test_generate_login_url(monkeypatch):
    session = FakeSession()
    monkeypatch.setattr(auth.fyersModel, "SessionModel", lambda *a, **k: session)

    url = auth.generate_login_url()

    assert url == "url"
