"""API contract and schema validation test suite using JSON Schema Draft-07.

Validates that responses strictly conform to canonical contract definitions
independently of runtime application code and Pydantic data models.
"""

from __future__ import annotations

from typing import Any

import pytest
from jsonschema import ValidationError

from api_framework.factories.booking_factory import BookingFactory
from api_framework.schemas import validate_schema
from api_framework.services.auth_service import AuthService
from api_framework.services.booking_service import BookingService
from api_framework.utils.resource_tracker import ResourceTracker
from config.settings import Settings


@pytest.mark.contract
class TestAPIContracts:
    """Validate JSON responses against canonical JSON Schema Draft-07 contracts."""

    def test_create_booking_response_contract(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify POST /booking response conforms to CreateBookingResponseSchema."""
        payload = booking_factory.build_valid()
        resp, parsed = booking_service.create_booking(payload)
        assert resp.status_code == 200
        assert parsed is not None

        resource_tracker.register(
            f"Contract Booking {parsed.bookingid}",
            lambda: booking_service.delete_booking(parsed.bookingid, token=auth_token),
        )

        data = resp.json()
        # Strictly validates structure, field types, and required properties
        validate_schema(data, "booking_response.schema.json")

    def test_get_booking_detail_response_contract(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify GET /booking/{id} response conforms to BookingSchema."""
        booking_id, _ = created_booking
        resp, _ = booking_service.get_booking(booking_id)
        assert resp.status_code == 200

        data = resp.json()
        validate_schema(data, "booking.schema.json")

    def test_list_booking_ids_response_contract(
        self,
        booking_service: BookingService,
    ) -> None:
        """Verify GET /booking response conforms to BookingListSchema."""
        resp, _ = booking_service.list_booking_ids()
        assert resp.status_code == 200

        data = resp.json()
        # Verify collection contract
        validate_schema(data, "booking_list.schema.json")

    def test_auth_success_response_contract(
        self,
        auth_service: AuthService,
        settings: Settings,
    ) -> None:
        """Verify successful POST /auth response conforms to AuthSuccessSchema."""
        resp, _ = auth_service.authenticate(
            username=settings.auth.username,
            password=settings.auth.password,
        )
        assert resp.status_code == 200
        data = resp.json()
        validate_schema(data, "auth.schema.json")

    def test_auth_failure_response_contract(
        self,
        auth_service: AuthService,
    ) -> None:
        """Verify failed POST /auth response conforms to AuthFailureSchema."""
        resp, _ = auth_service.authenticate(
            username="invalid_username",
            password="invalid_password",
        )
        assert resp.status_code == 200
        data = resp.json()
        validate_schema(data, "auth_failure.schema.json")

    def test_contract_validation_rejects_missing_mandatory_field(self) -> None:
        """Negative contract verification: Ensure validator detects missing mandatory properties."""
        corrupted_data = {
            "firstname": "John",
            # "lastname" missing
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_schema(corrupted_data, "booking.schema.json")

        assert "'lastname' is a required property" in str(exc_info.value)

    def test_contract_validation_rejects_incorrect_data_type(self) -> None:
        """Negative contract verification: Ensure validator detects schema type violations."""
        corrupted_data = {
            "firstname": "John",
            "lastname": "Doe",
            "totalprice": "string_not_integer",  # Invalid type
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
        }
        with pytest.raises(ValidationError) as exc_info:
            validate_schema(corrupted_data, "booking.schema.json")

        assert "'string_not_integer' is not of type 'integer'" in str(exc_info.value)
