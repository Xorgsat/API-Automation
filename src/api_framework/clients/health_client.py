"""Health check client for system availability validation."""

from __future__ import annotations

import requests

from api_framework.clients.base_client import BaseAPIClient


class HealthClient:
    """Client for Restful-Booker health check endpoints."""

    def __init__(self, client: BaseAPIClient) -> None:
        self.client = client

    def ping(self, **kwargs) -> requests.Response:
        """Call GET /ping to verify API availability.

        Note: Restful-Booker returns HTTP 201 Created and text 'Created'.
        """
        return self.client.get("/ping", **kwargs)
