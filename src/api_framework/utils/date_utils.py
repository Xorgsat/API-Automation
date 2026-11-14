"""Date utilities for generating realistic, boundary, and edge-case booking dates.

Ensures deterministic date generation and handles ISO-8601 formatting (YYYY-MM-DD).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta


def format_date(d: date) -> str:
    """Format a date object as YYYY-MM-DD."""
    return d.strftime("%Y-%m-%d")


def parse_date(date_str: str) -> date:
    """Parse a YYYY-MM-DD date string into a date object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def get_future_dates(days_ahead: int = 7, duration_days: int = 5) -> tuple[str, str]:
    """Generate checkin and checkout dates starting `days_ahead` from today."""
    today = date.today()
    checkin = today + timedelta(days=days_ahead)
    checkout = checkin + timedelta(days=duration_days)
    return format_date(checkin), format_date(checkout)


def get_past_dates(days_ago: int = 30, duration_days: int = 5) -> tuple[str, str]:
    """Generate past checkin and checkout dates."""
    today = date.today()
    checkin = today - timedelta(days=days_ago)
    checkout = checkin + timedelta(days=duration_days)
    return format_date(checkin), format_date(checkout)


def get_same_day_dates(days_ahead: int = 10) -> tuple[str, str]:
    """Generate same checkin and checkout date (boundary case)."""
    target = date.today() + timedelta(days=days_ahead)
    d_str = format_date(target)
    return d_str, d_str


def get_reversed_dates(days_ahead: int = 10, reversed_by_days: int = 3) -> tuple[str, str]:
    """Generate checkin date AFTER checkout date (negative/invalid scenario)."""
    base = date.today() + timedelta(days=days_ahead)
    checkin = base + timedelta(days=reversed_by_days)
    checkout = base
    return format_date(checkin), format_date(checkout)


def get_leap_year_dates() -> tuple[str, str]:
    """Generate a leap year boundary date (e.g. Feb 28 to Feb 29)."""
    return "2028-02-28", "2028-02-29"
