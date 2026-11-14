"""Authentication client for token generation and credential testing."""

from __future__ import annotations

from typing import Any

import requests

from api_framework.clients.base_client import BaseAPIClient


class AuthClient:
    """Client for Restful-Booker authentication endpoints."""

    def __init__(self, client: BaseAPIClient) -> None:
        self.client = client

    def create_token(
        self,
        username: str | None = None,
        password: str | None = None,
        raw_payload: Any = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call POST /auth to generate an authentication token."""
        if raw_payload is not None:
            if isinstance(raw_payload, str):
                req_headers = {"Content-Type": "application/json"}
                if headers:
                    req_headers.update(headers)
                return self.client.post("/auth", data=raw_payload, headers=req_headers)
            return self.client.post("/auth", json_data=raw_payload, headers=headers)

        payload: dict[str, Any] = {}
        if username is not None:
            payload["username"] = username
        if password is not None:
            payload["password"] = password

        return self.client.post("/auth", json_data=payload, headers=headers)
