"""Concurrency and parallel operations test suite validating thread safety and isolation."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import pytest

from api_framework.assertions.booking_assertions import assert_booking_matches
from api_framework.factories.booking_factory import BookingFactory
from api_framework.services.auth_service import AuthService
from api_framework.services.booking_service import BookingService
from api_framework.utils.resource_tracker import ResourceTracker
from config.settings import Settings


@pytest.mark.concurrency
class TestConcurrentOperations:
    """Validate behavior under controlled multi-threaded execution."""

    def test_concurrent_booking_creations_unique_isolation(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify multiple threads can concurrently create bookings without collisions."""
        worker_count = 5
        payloads = [booking_factory.build_valid() for _ in range(worker_count)]
        created_ids: list[int] = []

        def worker(payload: dict[str, Any]) -> int:
            resp, parsed = booking_service.create_booking(payload)
            assert resp.status_code == 200
            assert parsed is not None
            return parsed.bookingid

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(worker, p) for p in payloads]
            for f in as_completed(futures):
                bid = f.result()
                created_ids.append(bid)
                resource_tracker.register(
                    f"Concurrent Booking {bid}",
                    lambda b=bid: booking_service.delete_booking(b, token=auth_token),
                )

        assert len(created_ids) == worker_count
        # All created IDs must be unique
        assert len(set(created_ids)) == worker_count

    def test_concurrent_reads_on_single_resource(
        self,
        booking_service: BookingService,
        created_booking: tuple[int, dict[str, Any]],
    ) -> None:
        """Verify concurrent read requests on a single resource all succeed consistently."""
        booking_id, expected_data = created_booking
        read_count = 6

        def read_worker() -> tuple[int, Any]:
            resp, parsed = booking_service.get_booking(booking_id)
            return resp.status_code, parsed

        with ThreadPoolExecutor(max_workers=read_count) as executor:
            futures = [executor.submit(read_worker) for _ in range(read_count)]
            for f in as_completed(futures):
                status_code, parsed = f.result()
                assert status_code == 200
                assert parsed is not None
                assert_booking_matches(parsed, expected_data)

    def test_concurrent_updates_on_independent_resources(
        self,
        booking_service: BookingService,
        booking_factory: BookingFactory,
        auth_token: str,
        resource_tracker: ResourceTracker,
    ) -> None:
        """Verify parallel updates to independently owned resources do not cross-contaminate."""
        target_count = 3
        # Create resources
        records: list[tuple[int, dict[str, Any]]] = []
        for i in range(target_count):
            p = booking_factory.build_valid(firstname=f"Orig_{i}")
            _, created = booking_service.create_booking(p)
            assert created is not None
            bid = created.bookingid
            records.append((bid, p))
            resource_tracker.register(
                f"Independent Update Booking {bid}",
                lambda b=bid: booking_service.delete_booking(b, token=auth_token),
            )

        def update_worker(bid: int, idx: int) -> tuple[int, str]:
            new_name = f"UpdatedConcurrently_{idx}"
            patch = {"firstname": new_name}
            resp, parsed = booking_service.partial_update_booking(bid, payload=patch, token=auth_token)
            assert resp.status_code == 200
            assert parsed is not None
            return bid, parsed.firstname

        with ThreadPoolExecutor(max_workers=target_count) as executor:
            futures = [
                executor.submit(update_worker, bid, idx)
                for idx, (bid, _) in enumerate(records)
            ]
            for f in as_completed(futures):
                bid, final_first = f.result()
                assert final_first.startswith("UpdatedConcurrently_")

    def test_concurrent_authentication_requests(
        self,
        auth_service: AuthService,
        settings: Settings,
    ) -> None:
        """Verify concurrent authentication calls all succeed and generate valid session tokens."""
        auth_count = 4

        def auth_worker() -> str:
            resp, parsed = auth_service.authenticate(
                username=settings.auth.username,
                password=settings.auth.password,
            )
            assert resp.status_code == 200
            assert parsed is not None
            return parsed.token

        with ThreadPoolExecutor(max_workers=auth_count) as executor:
            futures = [executor.submit(auth_worker) for _ in range(auth_count)]
            tokens = [f.result() for f in as_completed(futures)]

        assert len(tokens) == auth_count
        for t in tokens:
            assert len(t) >= 10
