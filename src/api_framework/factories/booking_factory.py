"""Booking test data factory.

Provides flexible, deterministic test data generation for positive, negative,
boundary, and exploratory testing scenarios.
"""

from __future__ import annotations

from typing import Any

from api_framework.models.booking import BookingRequest
from api_framework.utils.date_utils import (
    get_future_dates,
    get_leap_year_dates,
    get_reversed_dates,
    get_same_day_dates,
)
from api_framework.utils.random_data import RandomDataGenerator, default_generator


class BookingFactory:
    """Factory for constructing booking test payloads."""

    def __init__(self, generator: RandomDataGenerator | None = None) -> None:
        self.gen = generator or default_generator

    def build_valid(
        self,
        firstname: str | None = None,
        lastname: str | None = None,
        totalprice: int | None = None,
        depositpaid: bool | None = None,
        checkin: str | None = None,
        checkout: str | None = None,
        additionalneeds: str | None = None,
    ) -> dict[str, Any]:
        """Construct a standard valid booking dictionary."""
        def_checkin, def_checkout = get_future_dates(days_ahead=14, duration_days=5)
        payload = {
            "firstname": firstname if firstname is not None else self.gen.first_name("Auto"),
            "lastname": lastname if lastname is not None else self.gen.last_name("Guest"),
            "totalprice": totalprice if totalprice is not None else self.gen.total_price(100, 1500),
            "depositpaid": depositpaid if depositpaid is not None else True,
            "bookingdates": {
                "checkin": checkin or def_checkin,
                "checkout": checkout or def_checkout,
            },
            "additionalneeds": additionalneeds or self.gen.additional_needs(),
        }
        return payload

    def build_valid_model(self, **kwargs: Any) -> BookingRequest:
        """Construct a validated BookingRequest Pydantic model."""
        payload = self.build_valid(**kwargs)
        return BookingRequest(**payload)

    def build_minimal(self) -> dict[str, Any]:
        """Construct a minimal valid booking payload without optional fields."""
        c_in, c_out = get_future_dates(days_ahead=3, duration_days=2)
        return {
            "firstname": self.gen.first_name("Min"),
            "lastname": self.gen.last_name("Guest"),
            "totalprice": 50,
            "depositpaid": False,
            "bookingdates": {
                "checkin": c_in,
                "checkout": c_out,
            },
        }

    def build_boundary_prices(self, price: int) -> dict[str, Any]:
        """Construct a booking with a specific boundary price (e.g. 0, max integer)."""
        data = self.build_valid()
        data["totalprice"] = price
        return data

    def build_boundary_strings(self, length: int) -> dict[str, Any]:
        """Construct a booking with first and last names of extreme length."""
        data = self.build_valid()
        long_str = self.gen.string_of_length(length)
        data["firstname"] = long_str
        data["lastname"] = long_str
        return data

    def build_special_characters(self) -> dict[str, Any]:
        """Construct a booking with special symbols and punctuation."""
        data = self.build_valid()
        special = self.gen.special_character_string()
        data["firstname"] = f"Sym_{special[:8]}"
        data["lastname"] = f"Punc_{special[8:16]}"
        data["additionalneeds"] = special
        return data

    def build_unicode(self) -> dict[str, Any]:
        """Construct a booking with multi-byte international Unicode characters."""
        data = self.build_valid()
        uni = self.gen.unicode_string()
        data["firstname"] = f"名_{uni[:10]}"
        data["lastname"] = f"姓_{uni[10:20]}"
        data["additionalneeds"] = uni
        return data

    def build_same_day_dates(self) -> dict[str, Any]:
        """Construct a booking where checkin equals checkout (same-day boundary)."""
        data = self.build_valid()
        c_in, c_out = get_same_day_dates(days_ahead=20)
        data["bookingdates"] = {"checkin": c_in, "checkout": c_out}
        return data

    def build_reversed_dates(self) -> dict[str, Any]:
        """Construct a booking with checkin AFTER checkout (temporal anomaly)."""
        data = self.build_valid()
        c_in, c_out = get_reversed_dates(days_ahead=20, reversed_by_days=5)
        data["bookingdates"] = {"checkin": c_in, "checkout": c_out}
        return data

    def build_leap_year(self) -> dict[str, Any]:
        """Construct a booking spanning a leap year February 29th date."""
        data = self.build_valid()
        c_in, c_out = get_leap_year_dates()
        data["bookingdates"] = {"checkin": c_in, "checkout": c_out}
        return data


# Default factory instance
default_booking_factory = BookingFactory()
