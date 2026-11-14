"""Authentication manager for handling credentials, tokens, and headers."""

from __future__ import annotations

import base64
import logging
import threading

from api_framework.clients.auth_client import AuthClient
from config.settings import Settings

logger = logging.getLogger("api_framework.auth")


class AuthManager:
    """Manages authentication tokens, cookies, and HTTP Basic Auth credentials."""

    def __init__(self, auth_client: AuthClient, settings: Settings) -> None:
        self.auth_client = auth_client
        self.settings = settings
        self._cached_token: str | None = None
        self._lock = threading.Lock()

    def get_token(self, force_refresh: bool = False) -> str:
        """Retrieve a valid session token, using thread-safe caching."""
        with self._lock:
            if self._cached_token and not force_refresh:
                return self._cached_token

            resp = self.auth_client.create_token(
                username=self.settings.auth.username,
                password=self.settings.auth.password,
            )
            if resp.status_code != 200:
                raise RuntimeError(
                    f"Authentication request failed with status {resp.status_code}: {resp.text}"
                )

            data = resp.json()
            if "token" not in data:
                raise RuntimeError(f"Token missing from auth response: {data}")

            self._cached_token = data["token"]
            logger.info("Successfully acquired new session token")
            return self._cached_token

    def get_cookie_header(self, token: str | None = None) -> dict[str, str]:
        """Construct Cookie header dictionary."""
        tok = token or self.get_token()
        return {"Cookie": f"token={tok}"}

    def get_basic_auth_header(
        self,
        username: str | None = None,
        password: str | None = None,
    ) -> dict[str, str]:
        """Construct HTTP Basic Authentication header dictionary."""
        user = username or self.settings.auth.username
        passwd = password or self.settings.auth.password
        raw = f"{user}:{passwd}".encode()
        encoded = base64.b64encode(raw).decode("ascii")
        return {"Authorization": f"Basic {encoded}"}

    def invalidate_token(self) -> None:
        """Clear cached token."""
        with self._lock:
            self._cached_token = None
