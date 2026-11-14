"""Authentication service handling token acquisition and auth workflows."""

from __future__ import annotations

from typing import Any

import requests

from api_framework.clients.auth_client import AuthClient
from api_framework.models.auth import AuthFailureResponse, AuthSuccessResponse


class AuthService:
    """Service abstraction for authentication workflows."""

    def __init__(self, client: AuthClient) -> None:
        self.client = client

    def authenticate(
        self,
        username: str | None = None,
        password: str | None = None,
        raw_payload: Any = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[requests.Response, AuthSuccessResponse | AuthFailureResponse | None]:
        """Authenticate against the API and parse response model if JSON."""
        resp = self.client.create_token(
            username=username,
            password=password,
            raw_payload=raw_payload,
            headers=headers,
        )

        parsed: AuthSuccessResponse | AuthFailureResponse | None = None
        if resp.status_code == 200:
            try:
                data = resp.json()
                if "token" in data:
                    parsed = AuthSuccessResponse(**data)
                elif "reason" in data:
                    parsed = AuthFailureResponse(**data)
            except Exception:
                pass

        return resp, parsed
