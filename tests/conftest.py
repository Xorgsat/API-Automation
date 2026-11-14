"""Root pytest fixtures and test lifecycle hooks for API Automation."""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Any

import pytest

from api_framework.auth.auth_manager import AuthManager
from api_framework.clients.auth_client import AuthClient
from api_framework.clients.base_client import BaseAPIClient
from api_framework.clients.booking_client import BookingClient
from api_framework.clients.health_client import HealthClient
from api_framework.factories.booking_factory import BookingFactory, default_booking_factory
from api_framework.services.auth_service import AuthService
from api_framework.services.booking_service import BookingService
from api_framework.services.health_service import HealthService
from api_framework.utils.resource_tracker import ResourceTracker
from config.settings import Settings, get_settings

logger = logging.getLogger("api_framework.conftest")


# ---------------------------------------------------------------------------
# Pytest Hooks & Report Customization
# ---------------------------------------------------------------------------


def pytest_configure(config: pytest.Config) -> None:
    """Register framework metadata in pytest configuration."""
    settings = get_settings()
    if hasattr(config, "_metadata"):
        config._metadata["Target API"] = "Restful-Booker"
        config._metadata["Base URL"] = settings.base_url
        config._metadata["Environment"] = settings.environment
        config._metadata["Timeout"] = f"{settings.timeout}s"


def pytest_html_report_title(report: Any) -> None:
    """Set custom title for pytest-html report."""
    report.title = "API Quality Engineering - Restful-Booker Test Report"


# ---------------------------------------------------------------------------
# Configuration & Core Clients
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Provide global application configuration."""
    return get_settings()


@pytest.fixture(scope="session")
def session_client(settings: Settings) -> Generator[BaseAPIClient, None, None]:
    """Provide session-scoped BaseAPIClient for connection re-use."""
    client = BaseAPIClient(
        base_url=settings.base_url,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
        retry_backoff=settings.retry_backoff,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def api_client(settings: Settings) -> Generator[BaseAPIClient, None, None]:
    """Provide function-scoped BaseAPIClient for completely isolated tests."""
    client = BaseAPIClient(
        base_url=settings.base_url,
        timeout=settings.timeout,
        max_retries=settings.max_retries,
        retry_backoff=settings.retry_backoff,
    )
    yield client
    client.close()


# ---------------------------------------------------------------------------
# Specialized Clients & Services
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def health_client(session_client: BaseAPIClient) -> HealthClient:
    """Provide HealthClient instance."""
    return HealthClient(session_client)


@pytest.fixture(scope="session")
def health_service(health_client: HealthClient) -> HealthService:
    """Provide HealthService instance."""
    return HealthService(health_client)


@pytest.fixture(scope="session")
def auth_client(session_client: BaseAPIClient) -> AuthClient:
    """Provide AuthClient instance."""
    return AuthClient(session_client)


@pytest.fixture(scope="session")
def auth_service(auth_client: AuthClient) -> AuthService:
    """Provide AuthService instance."""
    return AuthService(auth_client)


@pytest.fixture(scope="session")
def auth_manager(auth_client: AuthClient, settings: Settings) -> AuthManager:
    """Provide centralized AuthManager."""
    return AuthManager(auth_client, settings)


@pytest.fixture(scope="session")
def booking_client(session_client: BaseAPIClient) -> BookingClient:
    """Provide BookingClient instance."""
    return BookingClient(session_client)


@pytest.fixture(scope="session")
def booking_service(booking_client: BookingClient) -> BookingService:
    """Provide BookingService instance."""
    return BookingService(booking_client)


# ---------------------------------------------------------------------------
# Authentication Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def auth_token(auth_manager: AuthManager) -> str:
    """Provide a verified session authentication token."""
    return auth_manager.get_token()


@pytest.fixture(scope="session")
def auth_cookie_headers(auth_manager: AuthManager) -> dict[str, str]:
    """Provide cookie header with valid token."""
    return auth_manager.get_cookie_header()


@pytest.fixture(scope="session")
def basic_auth_headers(auth_manager: AuthManager) -> dict[str, str]:
    """Provide Authorization header with valid HTTP Basic credentials."""
    return auth_manager.get_basic_auth_header()


# ---------------------------------------------------------------------------
# Data Factories & Resource Lifecycles
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def booking_factory() -> BookingFactory:
    """Provide BookingFactory for test data construction."""
    return default_booking_factory


@pytest.fixture(scope="function")
def resource_tracker() -> Generator[ResourceTracker, None, None]:
    """Track resources created during a test and automatically clean them up."""
    tracker = ResourceTracker()
    yield tracker
    tracker.run_cleanups()


@pytest.fixture(scope="function")
def created_booking(
    booking_service: BookingService,
    booking_factory: BookingFactory,
    auth_token: str,
    resource_tracker: ResourceTracker,
) -> tuple[int, dict[str, Any]]:
    """Create a unique booking for testing, register teardown deletion, and yield (id, data)."""
    payload = booking_factory.build_valid()
    resp, parsed = booking_service.create_booking(payload)
    assert resp.status_code == 200, f"Setup failed to create booking: {resp.text}"
    assert parsed is not None, "Failed to parse created booking response"

    booking_id = parsed.bookingid

    # Register resilient cleanup
    def cleanup():
        booking_service.delete_booking(booking_id, token=auth_token)

    resource_tracker.register(f"Booking ID {booking_id}", cleanup)

    return booking_id, payload
