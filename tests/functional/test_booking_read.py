"""Functional test suite for Booking retrieval (GET /booking, GET /booking/{id})."""

from __future__ import annotations

from typing import Any

import pytest

from api_framework.assertions.booking_assertions import (
    assert_booking_id_in_list,
    assert_booking_matches,
)
from api_framework.assertions.response_assertions import (
    assert_content_type,
    assert_response_time_less_than,
    assert_status_code,
)
from api_framework.services.booking_service import BookingService


@pytest.mark.functional
class TestBookingRead:
    """Validate retrieval of booking resources by identifier and collection listings."""

    def test_get_existing_booking_by_id(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify retrieving an existing booking by ID returns 200 and accurate data."""
        booking_id, expected_data = created_booking

        resp, parsed = booking_service.get_booking(booking_id)
        assert_status_code(resp, 200)
        assert_content_type(resp, "application/json")
        assert_response_time_less_than(resp, 5.0)

        assert parsed is not None
        assert_booking_matches(parsed, expected_data)

    def test_get_nonexistent_booking_id(self, booking_service: BookingService) -> None:
        """Verify retrieving an absent booking ID returns HTTP 404 Not Found."""
        nonexistent_id = 999_999_999
        resp, parsed = booking_service.get_booking(nonexistent_id)

        assert_status_code(resp, 404)
        assert "Not Found" in resp.text
        assert parsed is None

    @pytest.mark.parametrize(
        "invalid_id",
        [0, -1, -999, "invalid_str", "!@#$"],
        ids=["zero_id", "negative_one", "large_negative", "alphanumeric", "special_symbols"],
    )
    def test_get_booking_invalid_identifier_formats(
        self,
        booking_service: BookingService,
        invalid_id: Any,
    ) -> None:
        """Verify non-integer or negative IDs return HTTP 404."""
        resp, parsed = booking_service.get_booking(invalid_id)
        assert_status_code(resp, 404)
        assert parsed is None

    def test_list_all_bookings_returns_collection(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify GET /booking returns 200 OK and a non-empty array of booking IDs."""
        booking_id, _ = created_booking

        resp, id_list = booking_service.list_booking_ids()
        assert_status_code(resp, 200)
        assert_content_type(resp, "application/json")
        assert id_list is not None
        assert len(id_list) > 0

        # Newly created booking should appear in the collection
        assert_booking_id_in_list(booking_id, id_list)
