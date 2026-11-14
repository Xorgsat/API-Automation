"""Smoke tests verifying API service availability and health check endpoint."""

from __future__ import annotations

import pytest

from api_framework.assertions.response_assertions import (
    assert_content_type,
    assert_response_time_less_than,
    assert_status_code,
)
from api_framework.services.health_service import HealthService


@pytest.mark.smoke
class TestHealthCheck:
    """Validate system availability via /ping endpoint."""

    def test_health_ping_status_and_body(self, health_service: HealthService) -> None:
        """Verify /ping returns HTTP 201 Created and body 'Created' as documented."""
        response = health_service.check_health()

        # Restful-Booker returns 201 Created for /ping
        assert_status_code(response, 201)
        assert response.text.strip() == "Created"

    def test_health_ping_response_time(self, health_service: HealthService) -> None:
        """Verify /ping responds within reasonable timeout threshold (5 seconds)."""
        response = health_service.check_health()
        assert_response_time_less_than(response, max_seconds=5.0)

    def test_health_ping_content_type(self, health_service: HealthService) -> None:
        """Verify Content-Type is text/plain on health ping response."""
        response = health_service.check_health()
        assert_content_type(response, "text/plain")

    def test_health_ping_unsupported_method_handling(self, session_client) -> None:
        """Verify unexpected HTTP method on /ping (e.g. POST) is rejected."""
        response = session_client.post("/ping", json_data={"ping": "test"})
        # Express router returns 404 or 405 for undefined route methods
        assert response.status_code in [404, 405]
