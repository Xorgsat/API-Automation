"""Pydantic models for Booking entities, requests, and responses.

Maintains strict separation between client-side request construction
and server-side response validation.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from api_framework.models.booking_dates import BookingDates


class BookingRequest(BaseModel):
    """Payload model for creating or updating a booking."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    firstname: str = Field(..., min_length=1, description="Guest first name")
    lastname: str = Field(..., min_length=1, description="Guest last name")
    totalprice: int = Field(..., description="Total price for the booking")
    depositpaid: bool = Field(..., description="Whether deposit has been paid")
    bookingdates: BookingDates = Field(..., description="Checkin and checkout dates")
    additionalneeds: str | None = Field(default=None, description="Optional special requests")

    def to_dict(self, exclude_none: bool = False) -> dict[str, Any]:
        """Convert model to dictionary for HTTP transmission."""
        return self.model_dump(exclude_none=exclude_none)


class BookingResponse(BaseModel):
    """Data model representing a booking returned by the API."""

    model_config = ConfigDict(extra="ignore")

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class CreateBookingResponse(BaseModel):
    """Response structure for POST /booking."""

    model_config = ConfigDict(extra="ignore")

    bookingid: int
    booking: BookingResponse


class BookingIDListing(BaseModel):
    """Item structure returned by GET /booking."""

    model_config = ConfigDict(extra="ignore")

    bookingid: int
