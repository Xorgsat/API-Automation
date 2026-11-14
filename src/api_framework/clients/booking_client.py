"""Booking client for executing HTTP CRUD and query operations on /booking."""

from __future__ import annotations

from typing import Any

import requests

from api_framework.clients.base_client import BaseAPIClient


class BookingClient:
    """Client for Restful-Booker booking endpoints."""

    def __init__(self, client: BaseAPIClient) -> None:
        self.client = client

    def get_booking_ids(
        self,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call GET /booking with optional query filters."""
        return self.client.get("/booking", params=params, headers=headers)

    def get_booking(
        self,
        booking_id: int | str,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call GET /booking/{id} to retrieve booking details."""
        return self.client.get(f"/booking/{booking_id}", headers=headers)

    def create_booking(
        self,
        payload: dict[str, Any] | None = None,
        raw_data: Any = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call POST /booking to create a new booking record."""
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)

        if raw_data is not None:
            return self.client.post("/booking", data=raw_data, headers=req_headers)
        return self.client.post("/booking", json_data=payload, headers=req_headers)

    def _prepare_auth_headers(
        self,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        """Construct headers with either cookie token or Authorization header."""
        out_headers = dict(headers or {})
        out_headers.setdefault("Content-Type", "application/json")
        out_headers.setdefault("Accept", "application/json")

        if token:
            out_headers["Cookie"] = f"token={token}"
        elif auth_header:
            out_headers["Authorization"] = auth_header
        return out_headers

    def update_booking(
        self,
        booking_id: int | str,
        payload: dict[str, Any] | None = None,
        raw_data: Any = None,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call PUT /booking/{id} for full booking update."""
        req_headers = self._prepare_auth_headers(token, auth_header, headers)
        if raw_data is not None:
            return self.client.put(f"/booking/{booking_id}", data=raw_data, headers=req_headers)
        return self.client.put(f"/booking/{booking_id}", json_data=payload, headers=req_headers)

    def partial_update_booking(
        self,
        booking_id: int | str,
        payload: dict[str, Any] | None = None,
        raw_data: Any = None,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call PATCH /booking/{id} for partial booking update."""
        req_headers = self._prepare_auth_headers(token, auth_header, headers)
        if raw_data is not None:
            return self.client.patch(f"/booking/{booking_id}", data=raw_data, headers=req_headers)
        return self.client.patch(f"/booking/{booking_id}", json_data=payload, headers=req_headers)

    def delete_booking(
        self,
        booking_id: int | str,
        token: str | None = None,
        auth_header: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        """Call DELETE /booking/{id} to remove a booking."""
        req_headers = self._prepare_auth_headers(token, auth_header, headers)
        return self.client.delete(f"/booking/{booking_id}", headers=req_headers)
