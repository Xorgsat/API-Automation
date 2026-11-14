"""Reusable HTTP response assertions with clear diagnostic failure details."""

from __future__ import annotations

from typing import Any

import requests


def _format_diagnostics(resp: requests.Response) -> str:
    """Format failure diagnostics including correlation ID, status, and truncated body."""
    corr_id = getattr(resp, "correlation_id", "N/A")
    elapsed = getattr(resp, "elapsed_seconds", 0.0)
    preview = resp.text[:400] if resp.text else "<empty body>"
    return (
        f"\n[DIAGNOSTICS] Method: {resp.request.method} {resp.request.url}"
        f"\n[DIAGNOSTICS] Status: {resp.status_code} | Elapsed: {elapsed:.3f}s | Correlation-ID: {corr_id}"
        f"\n[DIAGNOSTICS] Headers: {dict(resp.headers)}"
        f"\n[DIAGNOSTICS] Body: {preview}"
    )


def assert_status_code(response: requests.Response, expected_status: int | list[int]) -> None:
    """Assert response HTTP status matches expected code or one of expected codes."""
    if isinstance(expected_status, int):
        expected_status = [expected_status]

    diag = _format_diagnostics(response)
    assert (
        response.status_code in expected_status
    ), f"Expected status code {expected_status}, but received {response.status_code}.{diag}"


def assert_content_type(response: requests.Response, expected_type: str) -> None:
    """Assert response Content-Type contains expected MIME type."""
    content_type = response.headers.get("Content-Type", "")
    diag = _format_diagnostics(response)
    assert (
        expected_type.lower() in content_type.lower()
    ), f"Expected Content-Type containing '{expected_type}', but received '{content_type}'.{diag}"


def assert_response_time_less_than(response: requests.Response, max_seconds: float) -> None:
    """Assert that response elapsed time was within the threshold."""
    elapsed = getattr(response, "elapsed_seconds", response.elapsed.total_seconds())
    diag = _format_diagnostics(response)
    assert (
        elapsed <= max_seconds
    ), f"Response time {elapsed:.3f}s exceeded maximum allowed {max_seconds:.3f}s.{diag}"


def assert_header_present(response: requests.Response, header_name: str) -> None:
    """Assert header is present in response."""
    diag = _format_diagnostics(response)
    assert (
        header_name.lower() in [h.lower() for h in response.headers]
    ), f"Header '{header_name}' was not found in response headers.{diag}"


def assert_json_field(response: requests.Response, field_name: str, expected_val: Any) -> None:
    """Assert a top-level field in JSON response matches expected value."""
    diag = _format_diagnostics(response)
    try:
        data = response.json()
    except Exception as exc:
        raise AssertionError(f"Response body is not valid JSON: {exc}.{diag}") from exc

    assert field_name in data, f"Key '{field_name}' not present in response JSON: {data}.{diag}"
    actual_val = data[field_name]
    assert (
        actual_val == expected_val
    ), f"Field '{field_name}' mismatch: expected '{expected_val}', got '{actual_val}'.{diag}"
