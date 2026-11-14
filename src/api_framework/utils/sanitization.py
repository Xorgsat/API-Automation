"""Data sanitization utilities for safe logging and diagnostics.

Prevents authentication tokens, passwords, and sensitive headers from leaking
into console logs, pytest reports, or CI artifacts.
"""

from __future__ import annotations

import re
from typing import Any

SENSITIVE_HEADERS = {"cookie", "authorization", "token"}
SENSITIVE_KEYS = {"password", "token", "secret", "access_token"}


def mask_string(val: str, keep_start: int = 2, keep_end: int = 2) -> str:
    """Mask a string, leaving only outer characters for correlation."""
    if not val:
        return ""
    if len(val) <= (keep_start + keep_end):
        return "***"
    return f"{val[:keep_start]}***{val[-keep_end:]}"


def sanitize_headers(headers: dict[str, Any] | None) -> dict[str, str]:
    """Return a sanitized copy of headers with sensitive values masked."""
    if not headers:
        return {}
    sanitized: dict[str, str] = {}
    for k, v in headers.items():
        lower_k = str(k).lower()
        if lower_k in SENSITIVE_HEADERS:
            val_str = str(v)
            if lower_k == "cookie" and "token=" in val_str:
                # Mask the token inside the cookie string
                sanitized[str(k)] = re.sub(
                    r"token=([a-zA-Z0-9_-]+)",
                    lambda m: f"token={mask_string(m.group(1))}",
                    val_str,
                )
            elif lower_k == "authorization" and val_str.lower().startswith("basic "):
                sanitized[str(k)] = "Basic ***"
            else:
                sanitized[str(k)] = mask_string(val_str)
        else:
            sanitized[str(k)] = str(v)
    return sanitized


def sanitize_payload(payload: Any) -> Any:
    """Recursively mask sensitive keys in dict or list payloads."""
    if isinstance(payload, dict):
        cleaned: dict[str, Any] = {}
        for k, v in payload.items():
            if str(k).lower() in SENSITIVE_KEYS:
                cleaned[k] = mask_string(str(v)) if v is not None else None
            else:
                cleaned[k] = sanitize_payload(v)
        return cleaned
    elif isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    return payload
