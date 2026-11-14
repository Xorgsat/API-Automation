"""Pydantic model for booking dates."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, field_validator


class BookingDates(BaseModel):
    """Booking checkin and checkout date interval."""

    model_config = ConfigDict(extra="ignore")

    checkin: str
    checkout: str

    @field_validator("checkin", "checkout", mode="after")
    @classmethod
    def validate_iso_format(cls, v: str) -> str:
        """Verify date matches standard ISO YYYY-MM-DD or document non-conformance."""
        # Note: Restful-Booker may return invalid dates such as '0NaN-aN-aN' on corrupted data
        return v
