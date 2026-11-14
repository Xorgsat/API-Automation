"""Health service providing business operations for API availability checks."""

from __future__ import annotations

import requests

from api_framework.clients.health_client import HealthClient


class HealthService:
    """Service abstraction for API health operations."""

    def __init__(self, client: HealthClient) -> None:
        self.client = client

    def check_health(self) -> requests.Response:
        """Execute system health check."""
        return self.client.ping()
