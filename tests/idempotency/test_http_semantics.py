"""Test suite evaluating HTTP method semantics, safety, and idempotency."""

from __future__ import annotations

from typing import Any

import pytest

from api_framework.assertions.booking_assertions import assert_booking_matches
from api_framework.assertions.response_assertions import assert_status_code
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService
from api_framework.utils.resource_tracker import ResourceTracker


@pytest.mark.idempotency
class TestHTTPSemantics:
    """Validate HTTP verb semantics (safety, idempotency) according to RFC 9110."""

    def test_get_is_safe_and_idempotent(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify repeated GET requests do not alter server state and return identical representation."""
        booking_id, expected_data = created_booking

        # First read
        resp1, data1 = booking_service.get_booking(booking_id)
        assert_status_code(resp1, 200)

        # Second read
        resp2, data2 = booking_service.get_booking(booking_id)
        assert_status_code(resp2, 200)

        # Representation must be identical
        assert data1 == data2
        assert_booking_matches(data1, expected_data)

    def test_put_is_idempotent(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        created_booking: tuple[int, dict[str, Any]],
        auth_token: str,
    ) -> None:
        """Verify repeated identical PUT requests yield identical resulting resource state."""
        booking_id, _ = created_booking
        target_payload = booking_factory.build_valid(
            firstname="IdempotentName",
            totalprice=750,
        )

        # First PUT
        resp1, data1 = booking_service.update_booking(
            booking_id, payload=target_payload, token=auth_token
        )
        assert_status_code(resp1, 200)

        # Second identical PUT
        resp2, data2 = booking_service.update_booking(
            booking_id, payload=target_payload, token=auth_token
        )
        assert_status_code(resp2, 200)

        assert data1 == data2
        assert_booking_matches(data2, target_payload)

    def test_post_is_non_idempotent_creates_multiple_resources(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify submitting identical POST requests produces distinct resources with unique IDs."""
        fixed_payload = booking_factory.build_valid()

        # First POST
        resp1, created1 = booking_service.create_booking(fixed_payload)
        assert_status_code(resp1, 200)
        assert created1 is not None
        id1 = created1.bookingid

        # Second identical POST
        resp2, created2 = booking_service.create_booking(fixed_payload)
        assert_status_code(resp2, 200)
        assert created2 is not None
        id2 = created2.bookingid

        resource_tracker.register(f"POST Booking {id1}", lambda: booking_service.delete_booking(id1, token=auth_token))
        resource_tracker.register(f"POST Booking {id2}", lambda: booking_service.delete_booking(id2, token=auth_token))

        # Crucial HTTP semantic distinction: POST creates multiple distinct resources
        assert id1 != id2, f"Expected unique IDs for repeated POST requests, but both received {id1}"

    def test_delete_repeat_semantic_handling(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
    ) -> None:
        """Verify observable DELETE semantics on repeated execution.

        While RFC 9110 specifies DELETE should ideally be idempotent in effect (the resource remains gone),
        Restful-Booker returns 201 on the first call and 405 Method Not Allowed on subsequent calls.
        """
        payload = booking_factory.build_valid()
        _, created = booking_service.create_booking(payload)
        assert created is not None
        bid = created.bookingid

        first_delete = booking_service.delete_booking(bid, token=auth_token)
        assert_status_code(first_delete, 201)

        second_delete = booking_service.delete_booking(bid, token=auth_token)
        assert_status_code(second_delete, 405)
