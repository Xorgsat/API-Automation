"""Functional test suite for Booking query filtering (GET /booking?firstname=...&lastname=...)."""

from __future__ import annotations

from datetime import timedelta

import pytest

from api_framework.assertions.booking_assertions import (
    assert_booking_id_in_list,
)
from api_framework.assertions.response_assertions import assert_status_code
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService
from api_framework.utils.date_utils import format_date, parse_date
from api_framework.utils.resource_tracker import ResourceTracker


@pytest.mark.functional
class TestBookingFilters:
    """Validate query parameter filtering against /booking collection."""

    def test_filter_by_firstname(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify filtering by firstname returns matching booking ID."""
        unique_first = booking_factory.gen.first_name("FilterFirst")
        payload = booking_factory.build_valid(firstname=unique_first)

        _, created = booking_service.create_booking(payload)
        assert created is not None
        bid = created.bookingid
        resource_tracker.register(f"Booking {bid}", lambda: booking_service.delete_booking(bid, token=auth_token))

        resp, id_list = booking_service.list_booking_ids(params={"firstname": unique_first})
        assert_status_code(resp, 200)
        assert id_list is not None
        assert_booking_id_in_list(bid, id_list)

    def test_filter_by_lastname(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify filtering by lastname returns matching booking ID."""
        unique_last = booking_factory.gen.last_name("FilterLast")
        payload = booking_factory.build_valid(lastname=unique_last)

        _, created = booking_service.create_booking(payload)
        assert created is not None
        bid = created.bookingid
        resource_tracker.register(f"Booking {bid}", lambda: booking_service.delete_booking(bid, token=auth_token))

        resp, id_list = booking_service.list_booking_ids(params={"lastname": unique_last})
        assert_status_code(resp, 200)
        assert id_list is not None
        assert_booking_id_in_list(bid, id_list)

    def test_filter_by_combined_firstname_and_lastname(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify combined firstname and lastname filters narrow down exact matches."""
        unique_first = booking_factory.gen.first_name("ExactFirst")
        unique_last = booking_factory.gen.last_name("ExactLast")
        payload = booking_factory.build_valid(firstname=unique_first, lastname=unique_last)

        _, created = booking_service.create_booking(payload)
        assert created is not None
        bid = created.bookingid
        resource_tracker.register(f"Booking {bid}", lambda: booking_service.delete_booking(bid, token=auth_token))

        resp, id_list = booking_service.list_booking_ids(
            params={"firstname": unique_first, "lastname": unique_last}
        )
        assert_status_code(resp, 200)
        assert id_list is not None
        assert_booking_id_in_list(bid, id_list)

    def test_filter_by_checkin_date_semantics(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify checkin date filtering.

        Empirical Note: Restful-Booker's backend implementation evaluates:
        booking.checkin > query.checkin (strictly greater than).
        Therefore, querying for checkin date minus 1 day matches the resource.
        """
        payload = booking_factory.build_valid()
        checkin_date = payload["bookingdates"]["checkin"]
        # Calculate 1 day prior
        query_date = format_date(parse_date(checkin_date) - timedelta(days=1))

        _, created = booking_service.create_booking(payload)
        assert created is not None
        bid = created.bookingid
        resource_tracker.register(f"Booking {bid}", lambda: booking_service.delete_booking(bid, token=auth_token))

        resp, id_list = booking_service.list_booking_ids(params={"checkin": query_date})
        assert_status_code(resp, 200)
        assert id_list is not None
        assert_booking_id_in_list(bid, id_list)

    def test_filter_by_checkout_date_semantics(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify checkout date filtering matches records where checkout <= query.checkout."""
        payload = booking_factory.build_valid()
        checkout_date = payload["bookingdates"]["checkout"]

        _, created = booking_service.create_booking(payload)
        assert created is not None
        bid = created.bookingid
        resource_tracker.register(f"Booking {bid}", lambda: booking_service.delete_booking(bid, token=auth_token))

        resp, id_list = booking_service.list_booking_ids(params={"checkout": checkout_date})
        assert_status_code(resp, 200)
        assert id_list is not None
        assert_booking_id_in_list(bid, id_list)

    def test_filter_nonexistent_name_returns_empty_list(
        self,
        booking_service: BookingService,
    ) -> None:
        """Verify querying for a nonexistent name returns empty list []."""
        resp, id_list = booking_service.list_booking_ids(params={"firstname": "NonExistent_X9Z_NeverUsed"})
        assert_status_code(resp, 200)
        assert id_list == []

    def test_unsupported_pagination_parameters_ignored(
        self,
        booking_service: BookingService,
    ) -> None:
        """Verify pagination query parameters (limit, offset) are ignored by the server.

        Demonstrates that Restful-Booker does not implement pagination and returns the full dataset.
        """
        resp_all, list_all = booking_service.list_booking_ids()
        resp_paged, list_paged = booking_service.list_booking_ids(params={"limit": 5, "offset": 0})

        assert_status_code(resp_paged, 200)
        assert list_all is not None and list_paged is not None
        # The count returned with limit=5 is far greater than 5, confirming lack of pagination support
        assert len(list_paged) > 5
