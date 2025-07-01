"""Utility helpers to authenticate with the Fyers API."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any, Dict

from fyers_apiv3 import fyersModel

from .config import settings


def _build_session(grant_type: str = "authorization_code") -> fyersModel.SessionModel:
    """Create a configured SessionModel."""
    return fyersModel.SessionModel(
        client_id=settings.FYERS_APP_ID,
        secret_key=settings.FYERS_SECRET_KEY,
        redirect_uri=settings.FYERS_REDIRECT_URI,
        response_type="code",
        grant_type=grant_type,
    )


def generate_login_url() -> str:
    """Return the URL that begins the Fyers login flow."""
    session = _build_session()
    return session.generate_authcode()


async def exchange_auth_code(code: str) -> tuple[str, str]:
    """Exchange an authorization code for an access and refresh token."""
    session = _build_session()
    session.set_token(code)
    loop = asyncio.get_running_loop()
    response: Dict[str, Any] = await loop.run_in_executor(None, session.generate_token)
    return response.get("access_token", ""), response.get("refresh_token", "")


async def refresh_access_token(refresh_token: str, pin: str | None = None) -> str:
    """Refresh an expired access token."""
    session = _build_session("refresh_token")
    session.set_token(refresh_token)
    if pin is not None:
        # The fyers_apiv3 client does not explicitly support the PIN field but
        # accepts extra attributes which are sent in the request payload.
        session.pin = pin  # type: ignore[attr-defined]
    loop = asyncio.get_running_loop()
    response: Dict[str, Any] = await loop.run_in_executor(None, session.generate_token)
    return response.get("access_token", "")


def main(argv: list[str] | None = None) -> None:
    """Simple CLI helper for generating tokens."""
    parser = argparse.ArgumentParser(description="Fyers authentication helper")
    parser.add_argument("--auth-code", help="Authorization code from login redirect")
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Write the resulting token to the .env file",
    )
    args = parser.parse_args(argv)

    if args.auth_code:
        access, refresh = asyncio.run(exchange_auth_code(args.auth_code))
        if args.write_env:
            env = Path(".env")
            lines = []
            if env.exists():
                lines = [l.rstrip("\n") for l in env.read_text().splitlines() if l.strip()]
                lines = [
                    l
                    for l in lines
                    if not l.startswith("FYERS_ACCESS_TOKEN=")
                    and not l.startswith("FYERS_REFRESH_TOKEN=")
                ]
            lines.append(f"FYERS_ACCESS_TOKEN={access}")
            if refresh:
                lines.append(f"FYERS_REFRESH_TOKEN={refresh}")
            env.write_text("\n".join(lines) + "\n")
        print(access)
    else:
        print(generate_login_url())


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
