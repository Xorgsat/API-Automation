"""Negative test suite evaluating invalid JSON payloads and missing/corrupted fields."""

from __future__ import annotations

from typing import Any

import pytest

from api_framework.assertions.response_assertions import assert_status_code
from api_framework.services.booking_service import BookingService


@pytest.mark.negative
class TestInvalidPayloads:
    """Validate server response handling on malformed, missing, and corrupted request bodies."""

    def test_malformed_json_syntax(self, booking_service: BookingService) -> None:
        """Verify unparseable JSON syntax returns HTTP 400 Bad Request."""
        resp, _ = booking_service.create_booking(raw_data="{unclosed_json: true")
        assert_status_code(resp, 400)
        assert "Bad Request" in resp.text

    def test_empty_json_body_defect(self, booking_service: BookingService) -> None:
        """Verify empty JSON object returns 500 Internal Server Error.

        Defect Classification: Restful-Booker fails with unhandled 500 rather than 400/422
        when required top-level booking fields are completely omitted.
        """
        resp, _ = booking_service.create_booking(payload={})
        assert_status_code(resp, 500)

    @pytest.mark.parametrize(
        "missing_field_payload",
        [
            {"lastname": "Doe", "totalprice": 100, "depositpaid": True, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"}},
            {"firstname": "John", "totalprice": 100, "depositpaid": True, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"}},
            {"firstname": "John", "lastname": "Doe", "depositpaid": True, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"}},
            {"firstname": "John", "lastname": "Doe", "totalprice": 100, "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"}},
            {"firstname": "John", "lastname": "Doe", "totalprice": 100, "depositpaid": True},
        ],
        ids=[
            "missing_firstname",
            "missing_lastname",
            "missing_totalprice",
            "missing_depositpaid",
            "missing_bookingdates",
        ],
    )
    def test_missing_mandatory_fields_returns_error(
        self,
        booking_service: BookingService,
        missing_field_payload: dict[str, Any],
    ) -> None:
        """Verify omitting any mandatory property results in 500 Internal Server Error defect."""
        resp, _ = booking_service.create_booking(payload=missing_field_payload)
        assert_status_code(resp, 500)

    @pytest.mark.parametrize(
        "nested_date_payload",
        [
            {"firstname": "John", "lastname": "Doe", "totalprice": 100, "depositpaid": True, "bookingdates": {"checkout": "2026-01-05"}},
            {"firstname": "John", "lastname": "Doe", "totalprice": 100, "depositpaid": True, "bookingdates": {"checkin": "2026-01-01"}},
            {"firstname": "John", "lastname": "Doe", "totalprice": 100, "depositpaid": True, "bookingdates": {}},
        ],
        ids=["missing_checkin", "missing_checkout", "empty_bookingdates"],
    )
    def test_missing_nested_date_properties(
        self,
        booking_service: BookingService,
        nested_date_payload: dict[str, Any],
    ) -> None:
        """Verify omitting nested date properties results in 500 Internal Server Error."""
        resp, _ = booking_service.create_booking(payload=nested_date_payload)
        assert_status_code(resp, 500)

    def test_null_required_field_value_defect(self, booking_service: BookingService) -> None:
        """Verify passing explicit null for required string field results in 500 error."""
        payload = {
            "firstname": None,
            "lastname": "Doe",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
        }
        resp, _ = booking_service.create_booking(payload=payload)
        assert_status_code(resp, 500)

    def test_root_array_instead_of_object_defect(self, booking_service: BookingService) -> None:
        """Verify submitting an array at payload root causes 500 Internal Server Error."""
        resp, _ = booking_service.create_booking(raw_data='[{"firstname": "ArrayRoot"}]')
        assert_status_code(resp, 500)
