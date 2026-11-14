"""Base HTTP Client with structured logging, timing diagnostics, and sanitized tracing."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from api_framework.utils.sanitization import sanitize_headers, sanitize_payload

logger = logging.getLogger("api_framework.client")


class BaseAPIClient:
    """Thread-safe HTTP client wrapping requests.Session with timing and diagnostics."""

    def __init__(
        self,
        base_url: str,
        timeout: float = 15.0,
        max_retries: int = 2,
        retry_backoff: float = 0.5,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        headers = {
            "User-Agent": "python-api-quality-engineering/1.0",
            "Accept": "application/json",
        }
        if default_headers:
            headers.update(default_headers)
        self.session.headers.update(headers)

        # Configure safe connection pooling and selective retry for transport-level errors
        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=retry_backoff,
                status_forcelist=[502, 503, 504],
                allowed_methods=["GET", "HEAD", "OPTIONS"],  # Do NOT auto-retry POST/PUT/DELETE
                raise_on_status=False,
            )
            adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)

    def _build_url(self, endpoint: str) -> str:
        """Resolve endpoint to full URL."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        clean_endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{clean_endpoint}"

    def send_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json_data: Any = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        auth: tuple[str, str] | None = None,
        timeout: float | None = None,
    ) -> requests.Response:
        """Execute HTTP request with timing, correlation tracking, and structured logging."""
        url = self._build_url(endpoint)
        request_timeout = timeout if timeout is not None else self.timeout
        correlation_id = str(uuid.uuid4())[:8]

        req_headers = dict(headers or {})
        req_headers.setdefault("X-Correlation-ID", correlation_id)

        # Log sanitized outgoing request
        sanitized_hdrs = sanitize_headers({**dict(self.session.headers), **req_headers})
        sanitized_body = sanitize_payload(json_data) if json_data is not None else data
        logger.info(
            "[%s] HTTP %s %s | Headers: %s | Body: %s",
            correlation_id,
            method.upper(),
            url,
            sanitized_hdrs,
            sanitized_body,
        )

        start_time = time.perf_counter()
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=req_headers,
                cookies=cookies,
                auth=auth,
                timeout=request_timeout,
            )
        except requests.RequestException as exc:
            duration = time.perf_counter() - start_time
            logger.error(
                "[%s] HTTP %s %s FAILED after %.3fs: %s",
                correlation_id,
                method.upper(),
                url,
                duration,
                exc,
            )
            raise

        duration = time.perf_counter() - start_time
        # Attach custom metadata to response object for assertions and diagnostics
        response.elapsed_seconds = duration
        response.correlation_id = correlation_id

        # Safely log response preview
        resp_preview = response.text[:250] if response.text else "<empty>"
        logger.info(
            "[%s] HTTP %s %s -> Status: %d | Time: %.3fs | Body: %s",
            correlation_id,
            method.upper(),
            url,
            response.status_code,
            duration,
            resp_preview,
        )
        return response

    def get(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Execute GET request."""
        return self.send_request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Execute POST request."""
        return self.send_request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Execute PUT request."""
        return self.send_request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Execute PATCH request."""
        return self.send_request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> requests.Response:
        """Execute DELETE request."""
        return self.send_request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close underlying session."""
        self.session.close()
