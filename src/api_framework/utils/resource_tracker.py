"""Resource tracker for managing test-created resource lifecycles and cleanup resilience."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable

logger = logging.getLogger("api_framework.resources")


class ResourceTracker:
    """Thread-safe registry for created test resources requiring teardown cleanup."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cleanups: list[tuple[str, Callable[[], None]]] = []
        self._cleanup_failures: list[str] = []

    def register(self, resource_description: str, cleanup_fn: Callable[[], None]) -> None:
        """Register a resource cleanup action."""
        with self._lock:
            self._cleanups.append((resource_description, cleanup_fn))

    def run_cleanups(self) -> None:
        """Execute all registered cleanup functions in reverse order.

        Tolerates failures (already deleted resources, service errors) and logs them
        without masking test results.
        """
        with self._lock:
            items = list(reversed(self._cleanups))
            self._cleanups.clear()

        for description, cleanup_fn in items:
            try:
                cleanup_fn()
                logger.debug("Successfully cleaned up resource: %s", description)
            except Exception as exc:
                msg = f"Failed to cleanup resource '{description}': {exc}"
                logger.warning(msg)
                self._cleanup_failures.append(msg)

    @property
    def failures(self) -> list[str]:
        """Return list of recorded cleanup failure descriptions."""
        return list(self._cleanup_failures)
