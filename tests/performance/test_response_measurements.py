"""Lightweight API performance latency measurements and SLA threshold evaluations."""

from __future__ import annotations

import logging
from typing import Any

import pytest

from api_framework.factories.booking_factory import BookingFactory
from api_framework.reporting.report_helpers import calculate_latency_metrics, format_summary_table
from api_framework.services.auth_service import AuthService
from api_framework.services.booking_service import BookingService
from api_framework.services.health_service import HealthService
from api_framework.utils.resource_tracker import ResourceTracker
from config.settings import Settings

logger = logging.getLogger("api_framework.performance")


@pytest.mark.performance
class TestResponseMeasurements:
    """Execute lightweight latency measurements across critical API endpoints."""

    def test_health_check_latency_profile(self, health_service: HealthService) -> None:
        """Measure latency profile for GET /ping over multiple iterations."""
        sample_size = 5
        latencies: list[float] = []

        for _ in range(sample_size):
            resp = health_service.check_health()
            assert resp.status_code == 201
            latencies.append(getattr(resp, "elapsed_seconds", 0.0))

        metrics = calculate_latency_metrics(latencies)
        logger.info("\n--- HEALTH CHECK LATENCY PROFILE ---\n%s", format_summary_table(metrics))

        # Reasonable SLA for ping on active service: average < 2.0s
        assert metrics["mean"] < 2.0
        assert metrics["p95"] < 3.0

    def test_booking_retrieval_latency_profile(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Measure latency profile for GET /booking/{id}."""
        booking_id, _ = created_booking
        sample_size = 5
        latencies: list[float] = []

        for _ in range(sample_size):
            resp, _ = booking_service.get_booking(booking_id)
            assert resp.status_code == 200
            latencies.append(getattr(resp, "elapsed_seconds", 0.0))

        metrics = calculate_latency_metrics(latencies)
        logger.info("\n--- BOOKING RETRIEVAL LATENCY PROFILE ---\n%s", format_summary_table(metrics))

        assert metrics["mean"] < 2.5
        assert metrics["p95"] < 4.0

    def test_booking_creation_latency_profile(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Measure latency profile for POST /booking."""
        sample_size = 3
        latencies: list[float] = []

        for _ in range(sample_size):
            payload = booking_factory.build_valid()
            resp, created = booking_service.create_booking(payload)
            assert resp.status_code == 200
            assert created is not None
            bid = created.bookingid
            resource_tracker.register(
                f"Perf Booking {bid}",
                lambda b=bid: booking_service.delete_booking(b, token=auth_token),
            )
            latencies.append(getattr(resp, "elapsed_seconds", 0.0))

        metrics = calculate_latency_metrics(latencies)
        logger.info("\n--- BOOKING CREATION LATENCY PROFILE ---\n%s", format_summary_table(metrics))

        assert metrics["mean"] < 3.0

    def test_authentication_latency_profile(
        self,
        auth_service: AuthService,
        settings: Settings,
    ) -> None:
        """Measure latency profile for POST /auth."""
        sample_size = 3
        latencies: list[float] = []

        for _ in range(sample_size):
            resp, _ = auth_service.authenticate(
                username=settings.auth.username,
                password=settings.auth.password,
            )
            assert resp.status_code == 200
            latencies.append(getattr(resp, "elapsed_seconds", 0.0))

        metrics = calculate_latency_metrics(latencies)
        logger.info("\n--- AUTHENTICATION LATENCY PROFILE ---\n%s", format_summary_table(metrics))

        assert metrics["mean"] < 3.0
