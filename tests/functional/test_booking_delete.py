"""Functional test suite for Booking deletion (DELETE /booking/{id})."""

from __future__ import annotations

import pytest

from api_framework.assertions.response_assertions import (
    assert_response_time_less_than,
    assert_status_code,
)
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService


@pytest.mark.functional
class TestBookingDelete:
    """Validate resource deletion, post-deletion verification, and idempotency characteristics."""

    def test_delete_booking_with_cookie_token(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
    ) -> None:
        """Verify successful deletion of booking using Cookie token."""
        # Create resource explicitly within this test to test its full deletion
        payload = booking_factory.build_valid()
        create_resp, create_data = booking_service.create_booking(payload)
        assert create_resp.status_code == 200
        assert create_data is not None
        booking_id = create_data.bookingid

        delete_resp = booking_service.delete_booking(booking_id, token=auth_token)

        # Restful-Booker returns 201 Created on DELETE
        assert_status_code(delete_resp, 201)
        assert delete_resp.text.strip() == "Created"
        assert_response_time_less_than(delete_resp, 5.0)

        # Post-deletion verification: GET should return 404 Not Found
        get_resp, get_data = booking_service.get_booking(booking_id)
        assert_status_code(get_resp, 404)
        assert get_data is None

    def test_delete_booking_with_basic_auth(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        basic_auth_headers: dict[str, str],
    ) -> None:
        """Verify successful deletion using HTTP Basic Authentication header."""
        payload = booking_factory.build_valid()
        create_resp, create_data = booking_service.create_booking(payload)
        assert create_resp.status_code == 200
        assert create_data is not None
        booking_id = create_data.bookingid

        delete_resp = booking_service.delete_booking(
            booking_id, auth_header=basic_auth_headers["Authorization"]
        )
        assert_status_code(delete_resp, 201)

        # Verify resource is gone
        get_resp, _ = booking_service.get_booking(booking_id)
        assert_status_code(get_resp, 404)

    def test_repeated_deletion_handling(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
    ) -> None:
        """Verify second deletion attempt on already deleted resource returns 405 Method Not Allowed."""
        payload = booking_factory.build_valid()
        _, create_data = booking_service.create_booking(payload)
        assert create_data is not None
        booking_id = create_data.bookingid

        # First deletion succeeds
        first_del = booking_service.delete_booking(booking_id, token=auth_token)
        assert_status_code(first_del, 201)

        # Repeated deletion fails with 405 in Restful-Booker
        second_del = booking_service.delete_booking(booking_id, token=auth_token)
        assert_status_code(second_del, 405)

    def test_delete_nonexistent_booking_id(
        self,
        booking_service: BookingService,
        auth_token: str,
    ) -> None:
        """Verify deleting an absent ID returns 405 Method Not Allowed."""
        nonexistent_id = 999_999_999
        resp = booking_service.delete_booking(nonexistent_id, token=auth_token)
        assert_status_code(resp, 405)
