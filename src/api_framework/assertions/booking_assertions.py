"""Domain-specific assertions for booking models and payload structures."""

from __future__ import annotations

from typing import Any

from api_framework.models.booking import BookingResponse


def assert_booking_matches(
    actual: BookingResponse | dict[str, Any],
    expected: dict[str, Any],
) -> None:
    """Assert actual booking data matches expected field values."""
    actual_dict = actual.model_dump() if isinstance(actual, BookingResponse) else actual

    for key, expected_val in expected.items():
        assert key in actual_dict, f"Expected key '{key}' not found in actual booking: {actual_dict}"
        if key == "bookingdates":
            actual_dates = actual_dict["bookingdates"]
            assert actual_dates.get("checkin") == expected_val.get("checkin"), (
                f"Checkin date mismatch: expected {expected_val.get('checkin')}, "
                f"got {actual_dates.get('checkin')}"
            )
            assert actual_dates.get("checkout") == expected_val.get("checkout"), (
                f"Checkout date mismatch: expected {expected_val.get('checkout')}, "
                f"got {actual_dates.get('checkout')}"
            )
        else:
            assert actual_dict[key] == expected_val, (
                f"Booking field '{key}' mismatch: expected '{expected_val}', "
                f"got '{actual_dict[key]}'"
            )


def assert_booking_id_in_list(booking_id: int, booking_list: list[dict[str, Any]] | list[Any]) -> None:
    """Assert booking ID is present in list of bookings."""
    ids = [
        item.bookingid if hasattr(item, "bookingid") else item.get("bookingid")
        for item in booking_list
    ]
    assert booking_id in ids, f"Booking ID {booking_id} was not found in booking list ({len(ids)} items)"


def assert_booking_id_not_in_list(booking_id: int, booking_list: list[dict[str, Any]] | list[Any]) -> None:
    """Assert booking ID is NOT present in list of bookings."""
    ids = [
        item.bookingid if hasattr(item, "bookingid") else item.get("bookingid")
        for item in booking_list
    ]
    assert booking_id not in ids, f"Booking ID {booking_id} unexpectedly found in booking list"
