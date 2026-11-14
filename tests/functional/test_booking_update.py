"""Functional test suite for Booking updates (PUT /booking/{id}, PATCH /booking/{id})."""

from __future__ import annotations

from typing import Any

import pytest

from api_framework.assertions.booking_assertions import assert_booking_matches
from api_framework.assertions.response_assertions import (
    assert_content_type,
    assert_response_time_less_than,
    assert_status_code,
)
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService


@pytest.mark.functional
class TestBookingUpdate:
    """Validate full (PUT) and partial (PATCH) updates and persistence."""

    def test_full_update_with_cookie_token(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
        auth_token: str,
    ) -> None:
        """Verify full resource replacement via PUT using session token cookie."""
        booking_id, original_data = created_booking

        updated_payload = booking_factory.build_valid(
            firstname="UpdatedFirstName",
            lastname="UpdatedLastName",
            totalprice=888,
            depositpaid=False,
            additionalneeds="Champagne on arrival",
        )

        resp, parsed = booking_service.update_booking(
            booking_id=booking_id,
            payload=updated_payload,
            token=auth_token,
        )

        assert_status_code(resp, 200)
        assert_content_type(resp, "application/json")
        assert_response_time_less_than(resp, 5.0)

        assert parsed is not None
        assert_booking_matches(parsed, updated_payload)

        # Confirm persistence with an independent GET
        get_resp, get_data = booking_service.get_booking(booking_id)
        assert_status_code(get_resp, 200)
        assert_booking_matches(get_data, updated_payload)

    def test_full_update_with_basic_auth(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
        basic_auth_headers: dict[str, str],
    ) -> None:
        """Verify full update via PUT using HTTP Basic Authentication header."""
        booking_id, _ = created_booking

        updated_payload = booking_factory.build_valid(
            firstname="BasicAuthUpdated",
            totalprice=777,
        )

        resp, parsed = booking_service.update_booking(
            booking_id=booking_id,
            payload=updated_payload,
            auth_header=basic_auth_headers["Authorization"],
        )

        assert_status_code(resp, 200)
        assert parsed is not None
        assert_booking_matches(parsed, updated_payload)

    def test_partial_update_single_field_patch(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
        auth_token: str,
    ) -> None:
        """Verify updating a single field via PATCH modifies only the target property."""
        booking_id, original_data = created_booking

        patch_payload = {"firstname": "PatchedNameOnly"}
        resp, parsed = booking_service.partial_update_booking(
            booking_id=booking_id,
            payload=patch_payload,
            token=auth_token,
        )

        assert_status_code(resp, 200)
        assert parsed is not None
        assert parsed.firstname == "PatchedNameOnly"
        # Verify unchanged properties remained intact
        assert parsed.lastname == original_data["lastname"]
        assert parsed.totalprice == original_data["totalprice"]
        assert parsed.depositpaid == original_data["depositpaid"]

    def test_partial_update_nested_dates_patch(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
        auth_token: str,
    ) -> None:
        """Verify partial update of nested bookingdates via PATCH."""
        booking_id, original_data = created_booking

        patch_payload = {
            "bookingdates": {
                "checkin": "2027-10-01",
                "checkout": "2027-10-15",
            }
        }
        resp, parsed = booking_service.partial_update_booking(
            booking_id=booking_id,
            payload=patch_payload,
            token=auth_token,
        )

        assert_status_code(resp, 200)
        assert parsed is not None
        assert parsed.bookingdates.checkin == "2027-10-01"
        assert parsed.bookingdates.checkout == "2027-10-15"
        assert parsed.firstname == original_data["firstname"]

    def test_put_partial_payload_rejection(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
        auth_token: str,
    ) -> None:
        """Verify PUT with incomplete payload returns 400 Bad Request (PUT requires full entity)."""
        booking_id, _ = created_booking

        incomplete_payload = {"firstname": "Incomplete"}
        resp, _ = booking_service.update_booking(
            booking_id=booking_id,
            payload=incomplete_payload,
            token=auth_token,
        )

        assert_status_code(resp, 400)

    def test_update_nonexistent_booking_handling(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
    ) -> None:
        """Verify update on non-existent booking ID returns 405 Method Not Allowed."""
        nonexistent_id = 999_999_999
        payload = booking_factory.build_valid()

        resp, _ = booking_service.update_booking(
            booking_id=nonexistent_id,
            payload=payload,
            token=auth_token,
        )

        # Restful-Booker router returns 405 when target resource does not exist for PUT
        assert_status_code(resp, 405)
