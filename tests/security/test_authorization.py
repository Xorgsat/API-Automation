"""Security test suite validating authorization enforcement on mutating endpoints."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from api_framework.assertions.response_assertions import assert_status_code
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService


@pytest.mark.security
class TestAuthorizationEnforcement:
    """Verify write operations (PUT, PATCH, DELETE) strictly enforce authorization."""

    def test_put_without_authorization(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify PUT request without credentials is rejected with 403 Forbidden."""
        booking_id, _ = created_booking
        payload = booking_factory.build_valid()

        resp, _ = booking_service.update_booking(
            booking_id=booking_id,
            payload=payload,
            token=None,
            auth_header=None,
        )
        assert_status_code(resp, 403)
        assert "Forbidden" in resp.text

    def test_put_with_invalid_cookie_token(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify PUT request with an invalid/forged cookie token is rejected with 403."""
        booking_id, _ = created_booking
        payload = booking_factory.build_valid()

        resp, _ = booking_service.update_booking(
            booking_id=booking_id,
            payload=payload,
            token="invalid_token_deadbeef",
        )
        assert_status_code(resp, 403)

    def test_put_with_invalid_basic_auth(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify PUT request with invalid HTTP Basic Auth credentials is rejected with 403."""
        booking_id, _ = created_booking
        payload = booking_factory.build_valid()
        bad_auth = "Basic " + base64.b64encode(b"wrong:wrong").decode("ascii")

        resp, _ = booking_service.update_booking(
            booking_id=booking_id,
            payload=payload,
            auth_header=bad_auth,
        )
        assert_status_code(resp, 403)

    def test_patch_without_authorization(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify PATCH request without credentials returns 403 Forbidden."""
        booking_id, _ = created_booking

        resp, _ = booking_service.partial_update_booking(
            booking_id=booking_id,
            payload={"firstname": "Hacker"},
            token=None,
        )
        assert_status_code(resp, 403)

    def test_patch_with_invalid_cookie_token(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify PATCH request with an invalid cookie token returns 403 Forbidden."""
        booking_id, _ = created_booking

        resp, _ = booking_service.partial_update_booking(
            booking_id=booking_id,
            payload={"firstname": "Hacker"},
            token="expired_or_forged_token",
        )
        assert_status_code(resp, 403)

    def test_delete_without_authorization(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify DELETE request without credentials returns 403 Forbidden."""
        booking_id, _ = created_booking

        resp = booking_service.delete_booking(booking_id, token=None, auth_header=None)
        assert_status_code(resp, 403)

    def test_delete_with_invalid_cookie_token(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify DELETE request with an invalid cookie token returns 403 Forbidden."""
        booking_id, _ = created_booking

        resp = booking_service.delete_booking(booking_id, token="fake_token_12345")
        assert_status_code(resp, 403)

    def test_delete_with_invalid_basic_auth(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify DELETE request with incorrect Basic Auth returns 403 Forbidden."""
        booking_id, _ = created_booking
        bad_auth = "Basic " + base64.b64encode(b"admin:wrongpassword").decode("ascii")

        resp = booking_service.delete_booking(booking_id, auth_header=bad_auth)
        assert_status_code(resp, 403)

    def test_malformed_cookie_header_handling(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify malformed Cookie header (missing token key) is rejected with 403."""
        booking_id, _ = created_booking
        payload = booking_factory.build_valid()

        resp, _ = booking_service.update_booking(
            booking_id=booking_id,
            payload=payload,
            headers={"Cookie": "session_id=12345; auth=none"},
        )
        assert_status_code(resp, 403)

    def test_forbidden_error_does_not_leak_stack_traces(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify 403 Forbidden response contains no sensitive internals or stack traces."""
        booking_id, _ = created_booking

        resp = booking_service.delete_booking(booking_id, token="bad")
        assert_status_code(resp, 403)
        body_lower = resp.text.lower()
        for forbidden_term in ["node_modules", "at line", "syntaxerror", "express/lib", "var "]:
            assert forbidden_term not in body_lower, f"Information leakage detected: '{forbidden_term}' found in 403 response"
