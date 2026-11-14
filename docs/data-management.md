# Test Data Management & Lifecycle Isolation

## 1. Principles of Test Data Management

A key challenge when testing **Restful-Booker** is its public, multi-tenant nature and scheduled automated database wipes.
If automated tests rely on pre-existing records (e.g. assuming booking ID `1` always exists or retains specific fields), tests inevitably become flaky, order-dependent, and prone to race conditions.

To achieve enterprise-grade reliability, our framework enforces five principles:
1. **Zero Precondition Reliance**: Every test provisions whatever state it requires.
2. **Distinct Resource Ownership**: Every booking created has unique identifiers and names.
3. **Resilient Teardowns**: Resources are tracked and cleaned up regardless of whether assertions pass or fail.
4. **Non-Masking Cleanups**: Teardown failures are recorded as warnings and do not mask genuine test assertion results.
5. **Parallel Safety**: Parallel workers generate non-colliding entities.

---

## 2. Factory Pattern Implementation

The `BookingFactory` (`src/api_framework/factories/booking_factory.py`) provides declarative methods for constructing valid, boundary, and negative payloads:

```python
# Standard valid booking with controlled random attributes
payload = booking_factory.build_valid()

# Minimal valid payload (optional fields omitted)
minimal = booking_factory.build_minimal()

# Extreme price boundary (0, negative, max int)
boundary_price = booking_factory.build_boundary_prices(price=0)

# Extreme string lengths (up to 1,000 characters)
long_text = booking_factory.build_boundary_strings(length=1000)

# Multi-byte Unicode and special symbols
unicode_data = booking_factory.build_unicode()
```

---

## 3. Resilient Cleanup with `ResourceTracker`

### 3.1 The Problem of Naive Teardowns
In naive frameworks, teardown hooks execute hardcoded deletions. If the test itself was testing a deletion, the teardown attempt receives a `405 Method Not Allowed` or `404 Not Found`, crashing the test runner during teardown.

### 3.2 The Solution
Our `ResourceTracker` (`src/api_framework/utils/resource_tracker.py`):
1. Registers teardown callbacks dynamically as resources are created.
2. Executes cleanups in reverse order of creation.
3. Wraps each cleanup call in a resilient exception handler, capturing failures to a log and registry without failing the pytest teardown.

```python
@pytest.fixture(scope="function")
def created_booking(booking_service, booking_factory, auth_token, resource_tracker):
    payload = booking_factory.build_valid()
    resp, parsed = booking_service.create_booking(payload)
    booking_id = parsed.bookingid

    # Register cleanup
    resource_tracker.register(
        f"Booking {booking_id}",
        lambda: booking_service.delete_booking(booking_id, token=auth_token),
    )

    return booking_id, payload
```
