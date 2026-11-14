"""Negative test suite evaluating invalid identifiers across GET, PUT, and DELETE."""

from __future__ import annotations

from typing import Any

import pytest

from api_framework.assertions.response_assertions import assert_status_code
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService


@pytest.mark.negative
class TestInvalidIdentifiers:
    """Validate behavior when non-numeric, boundary, or corrupt IDs are supplied."""

    @pytest.mark.parametrize(
        "invalid_id",
        ["string_id", "!@#$%^", "0", "-1", "-999999", "999999999999999999"],
        ids=[
            "alpha_string",
            "special_characters",
            "zero",
            "negative_one",
            "large_negative",
            "overflow_integer",
        ],
    )
    def test_get_booking_with_invalid_id_returns_404(
        self,
        booking_service: BookingService,
        invalid_id: Any,
    ) -> None:
        """Verify GET with unresolvable or invalid identifier returns 404 Not Found."""
        resp, _ = booking_service.get_booking(invalid_id)
        assert_status_code(resp, 404)

    def test_float_id_truncation_backend_defect(
        self,
        booking_service: BookingService,
    ) -> None:
        """Verify and document API defect: Loose parseInt() truncation on decimal identifiers.

        Defect Classification: Target API Defect (BUG-007).
        When a client requests GET /booking/1.99 or 12.34, standard REST API design dictates
        returning HTTP 400 Bad Request or HTTP 404 Not Found due to non-integer type violation.
        However, Restful-Booker utilizes JavaScript's `parseInt(id, 10)`, which truncates the
        fractional portion, matching booking ID 12 and returning HTTP 200 OK.
        """
        resp, parsed = booking_service.get_booking("12.34")
        # Record observed defect behavior: status 200 due to parseInt truncation
        assert_status_code(resp, 200)
        assert parsed is not None

    @pytest.mark.parametrize(
        "invalid_id",
        ["string_id", "!@#$", "0", "-1"],
        ids=["alpha_string", "special_characters", "zero", "negative_one"],
    )
    def test_put_booking_with_invalid_id_returns_405(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        invalid_id: Any,
    ) -> None:
        """Verify PUT with invalid identifier returns 405 Method Not Allowed."""
        payload = booking_factory.build_valid()
        resp, _ = booking_service.update_booking(
            booking_id=invalid_id,
            payload=payload,
            token=auth_token,
        )
        assert_status_code(resp, 405)

    @pytest.mark.parametrize(
        "invalid_id",
        ["string_id", "!@#$", "0", "-1"],
        ids=["alpha_string", "special_characters", "zero", "negative_one"],
    )
    def test_delete_booking_with_invalid_id_returns_405(
        self,
        booking_service: BookingService,
        auth_token: str,
        invalid_id: Any,
    ) -> None:
        """Verify DELETE with invalid identifier returns 405 Method Not Allowed."""
        resp = booking_service.delete_booking(booking_id=invalid_id, token=auth_token)
        assert_status_code(resp, 405)
