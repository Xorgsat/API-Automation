"""Negative test suite evaluating Content-Type and Accept header negotiation."""

from __future__ import annotations

from typing import Any

import pytest

from api_framework.assertions.response_assertions import (
    assert_status_code,
)
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.booking_service import BookingService


@pytest.mark.negative
class TestInvalidHeaders:
    """Validate header handling, missing content-types, and content negotiation fallback."""

    def test_post_booking_missing_content_type_header(
        self,
        session_client,
        booking_factory: BookingFactory,
    ) -> None:
        """Verify omitting Content-Type header on POST /booking causes 500 error defect."""
        import json
        payload = booking_factory.build_valid()
        raw_bytes = json.dumps(payload).encode("utf-8")

        # Send raw request without Content-Type header
        resp = session_client.post("/booking", data=raw_bytes, headers={"Content-Type": None})
        assert_status_code(resp, 500)

    def test_post_booking_unsupported_content_type(
        self,
        session_client,
        booking_factory: BookingFactory,
    ) -> None:
        """Verify submitting JSON with Content-Type: text/plain causes 500 server defect."""
        import json
        payload = booking_factory.build_valid()
        raw_bytes = json.dumps(payload).encode("utf-8")

        resp = session_client.post("/booking", data=raw_bytes, headers={"Content-Type": "text/plain"})
        assert_status_code(resp, 500)

    def test_accept_header_fallback_on_unsupported_type(
        self,
        booking_service: BookingService,
    ) -> None:
        """Verify unsupported Accept: text/csv falls back to JSON rather than returning 406.

        Empirical Note: Restful-Booker does not implement HTTP 406 Not Acceptable.
        """
        resp, id_list = booking_service.list_booking_ids(headers={"Accept": "text/csv"})
        assert_status_code(resp, 200)
        assert id_list is not None

    def test_xml_content_negotiation_on_booking_read(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify GET /booking/{id} supports XML serialization when Accept: application/xml is requested."""
        booking_id, _ = created_booking

        resp, _ = booking_service.get_booking(booking_id, headers={"Accept": "application/xml"})
        assert_status_code(resp, 200)
        assert "<booking>" in resp.text
        assert "</booking>" in resp.text
