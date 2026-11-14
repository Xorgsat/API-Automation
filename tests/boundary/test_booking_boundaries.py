"""Boundary-Value Analysis (BVA) test suite for Booking data attributes."""

from __future__ import annotations

import pytest

from api_framework.assertions.booking_assertions import assert_booking_matches
from api_framework.assertions.response_assertions import assert_status_code
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService
from api_framework.utils.resource_tracker import ResourceTracker


@pytest.mark.boundary
class TestBookingBoundaries:
    """Validate behavior at the extreme limits of data boundaries."""

    @pytest.mark.parametrize(
        ("price", "test_id"),
        [
            (0, "zero_price"),
            (-1, "negative_one_price"),
            (-9999, "large_negative_price"),
            (1, "minimum_positive_price"),
            (2_147_483_647, "max_signed_32bit_int"),
        ],
    )
    def test_price_boundary_values(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
        price: int,
        test_id: str,
    ) -> None:
        """Verify handling of extreme numeric boundary prices.

        Defect Observation: Restful-Booker allows negative totalprice values without
        raising a validation error.
        """
        payload = booking_factory.build_boundary_prices(price=price)
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Price Boundary Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert parsed.booking.totalprice == price

    @pytest.mark.parametrize(
        ("str_len", "test_id"),
        [
            (1, "single_character"),
            (255, "standard_max_varchar"),
            (1000, "large_text_length"),
        ],
    )
    def test_string_length_boundaries(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
        str_len: int,
        test_id: str,
    ) -> None:
        """Verify handling of short and extremely long string lengths for guest names."""
        payload = booking_factory.build_boundary_strings(length=str_len)
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"String Boundary Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert len(parsed.booking.firstname) == str_len
        assert len(parsed.booking.lastname) == str_len

    def test_special_characters_boundary(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify handling of symbols, punctuation, and injection candidates in string fields."""
        payload = booking_factory.build_special_characters()
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Special Char Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert_booking_matches(parsed.booking, payload)

    def test_international_unicode_boundary(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify multi-byte international Unicode characters (CJK, Emojis, Diacritics)."""
        payload = booking_factory.build_unicode()
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Unicode Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert_booking_matches(parsed.booking, payload)

    def test_same_day_checkin_checkout_boundary(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify booking where checkin equals checkout (0-night stay)."""
        payload = booking_factory.build_same_day_dates()
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Same-day Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert (
            parsed.booking.bookingdates.checkin == parsed.booking.bookingdates.checkout
        )

    def test_reversed_dates_defect(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify behavior when checkin is after checkout.

        Defect Observation: Restful-Booker does not enforce temporal order validation
        (checkout > checkin) and stores reversed dates.
        """
        payload = booking_factory.build_reversed_dates()
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Reversed Dates Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert (
            parsed.booking.bookingdates.checkin > parsed.booking.bookingdates.checkout
        )

    def test_leap_year_boundary_date(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify handling of valid leap year date February 29th (2028-02-29)."""
        payload = booking_factory.build_leap_year()
        resp, parsed = booking_service.create_booking(payload)

        assert_status_code(resp, 200)
        assert parsed is not None
        resource_tracker.register(
            f"Leap Year Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )
        assert parsed.booking.bookingdates.checkout == "2028-02-29"
