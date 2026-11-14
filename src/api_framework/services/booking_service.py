"""Booking service coordinating domain operations on bookings."""

from __future__ import annotations

from typing import Any

import requests

from api_framework.clients.booking_client import BookingClient
from api_framework.models.booking import (
    BookingIDListing,
    BookingResponse,
    CreateBookingResponse,
)


class BookingService:
    """Service abstraction for booking domain workflows."""

    def __init__(self, client: BookingClient) -> None:
        self.client = client

    def create_booking(
        self,
        payload: dict[str, Any] | None = None,
        raw_data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[requests.Response, CreateBookingResponse | None]:
        """Create booking and attempt to parse CreateBookingResponse model."""
        resp = self.client.create_booking(payload=payload, raw_data=raw_data, headers=headers)
        parsed: CreateBookingResponse | None = None
        if resp.status_code == 200:
            try:
                parsed = CreateBookingResponse(**resp.json())
            except Exception:
                pass
        return resp, parsed

    def get_booking(
        self,
        booking_id: int | str,
        headers: dict[str, str] | None = None,
    ) -> tuple[requests.Response, BookingResponse | None]:
        """Retrieve booking details by ID and parse BookingResponse model."""
        resp = self.client.get_booking(booking_id=booking_id, headers=headers)
        parsed: BookingResponse | None = None
        if resp.status_code == 200:
            try:
                parsed = BookingResponse(**resp.json())
            except Exception:
                pass
        return resp, parsed

    def list_booking_ids(
        self,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[requests.Response, list[BookingIDListing] | None]:
        """Retrieve list of booking IDs matching optional query parameters."""
        resp = self.client.get_booking_ids(params=params, headers=headers)
        parsed: list[BookingIDListing] | None = None
        if resp.status_code == 200:
            try:
                parsed = [BookingIDListing(**item) for item in resp.json()]
            except Exception:
                pass
        return resp, parsed

    def update_booking(
        self,
        booking_id: int | str,
        payload: dict[str, Any] | None = None,
        raw_data: Any = None,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[requests.Response, BookingResponse | None]:
        """Fully update a booking (PUT) and parse BookingResponse."""
        resp = self.client.update_booking(
            booking_id=booking_id,
            payload=payload,
            raw_data=raw_data,
            token=token,
            auth_header=auth_header,
            headers=headers,
        )
        parsed: BookingResponse | None = None
        if resp.status_code == 200:
            try:
                parsed = BookingResponse(**resp.json())
            except Exception:
                pass
        return resp, parsed

    def partial_update_booking(
        self,
        booking_id: int | str,
        payload: dict[str, Any] | None = None,
        raw_data: Any = None,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[requests.Response, BookingResponse | None]:
        """Partially update a booking (PATCH) and parse BookingResponse."""
        resp = self.client.partial_update_booking(
            booking_id=booking_id,
            payload=payload,
            raw_data=raw_data,
            token=token,
            auth_header=auth_header,
            headers=headers,
        )
        parsed: BookingResponse | None = None
        if resp.status_code == 200:
            try:
                parsed = BookingResponse(**resp.json())
            except Exception:
                pass
        return resp, parsed

    def delete_booking(
        self,
        booking_id: int | str,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Delete booking by ID."""
        return self.client.delete_booking(
            booking_id=booking_id,
            token=token,
            auth_header=auth_header,
            headers=headers,
        )
