"""Functional test suite for Booking creation (POST /booking)."""

from __future__ import annotations

import pytest

from api_framework.assertions.booking_assertions import assert_booking_matches
from api_framework.assertions.response_assertions import (
    assert_content_type,
    assert_response_time_less_than,
    assert_status_code,
)
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService
from api_framework.utils.resource_tracker import ResourceTracker


@pytest.mark.functional
class TestBookingCreate:
    """Validate booking creation scenarios, persistence, and response structure."""

    def test_create_booking_valid_full_payload(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify successful creation of a booking with complete valid payload."""
        payload = booking_factory.build_valid()
        resp, parsed = booking_service.create_booking(payload)

        # Restful-Booker returns HTTP 200 OK on booking creation
        assert_status_code(resp, 200)
        assert_content_type(resp, "application/json")
        assert_response_time_less_than(resp, 5.0)

        assert parsed is not None
        assert parsed.bookingid > 0
        resource_tracker.register(
            f"Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )

        assert_booking_matches(parsed.booking, payload)

    def test_create_booking_minimal_payload(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify creation with only mandatory fields (additionalneeds omitted)."""
        payload = booking_factory.build_minimal()
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )

        assert_booking_matches(parsed.booking, payload)

    def test_create_booking_persistence_read_after_write(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify immediate read-after-write consistency for newly created resource."""
        payload = booking_factory.build_valid()
        create_resp, create_data = booking_service.create_booking(payload)
        assert_status_code(create_resp, 200)
        assert create_data is not None
        booking_id = create_data.bookingid

        resource_tracker.register(
            f"Booking {booking_id}",
            lambda: booking_service.delete_booking(booking_id, token=auth_token),
        )

        # Fetch newly created booking
        get_resp, get_data = booking_service.get_booking(booking_id)
        assert_status_code(get_resp, 200)
        assert get_data is not None
        assert_booking_matches(get_data, payload)

    @pytest.mark.parametrize(
        ("firstname", "lastname", "price", "deposit", "needs"),
        [
            ("Alice", "Wonderland", 300, True, "Breakfast"),
            ("Bob", "Builder", 120, False, "Late Checkout"),
            ("Charlie", "Chaplin", 999, True, None),
            ("Diana", "Prince", 50, False, "Quiet room on high floor"),
        ],
        ids=["full_deposit_true", "deposit_false", "no_additional_needs", "long_special_needs"],
    )
    def test_create_booking_parametrized_variations(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
        firstname: str,
        lastname: str,
        price: int,
        deposit: bool,
        needs: str | None,
    ) -> None:
        """Verify booking creation across diverse realistic field combinations."""
        payload = booking_factory.build_valid(
            firstname=firstname,
            lastname=lastname,
            totalprice=price,
            depositpaid=deposit,
            additionalneeds=needs,
        )
        resp, parsed = booking_service.create_booking(payload)
        assert_status_code(resp, 200)
        assert parsed is not None

        resource_tracker.register(
            f"Param Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert_booking_matches(parsed.booking, payload)
