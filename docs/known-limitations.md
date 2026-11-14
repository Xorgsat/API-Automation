# Known API Limitations and Defect Catalogue

This document provides a comprehensive catalogue of verified behavioral defects, architectural limitations, and specification non-conformances observed in **Restful-Booker** (`https://restful-booker.herokuapp.com`).

---

## 1. Verified Target API Defects

### BUG-001: Health Check Endpoint Returns HTTP 201 Created
- **Endpoint**: `GET /ping`
- **Expected Behavior**: HTTP `200 OK` with standard health status payload.
- **Observed Behavior**: HTTP `201 Created` with text body `"Created"`.
- **Classification**: Target API Defect / Spec Deviation.
- **Remediation**: Update router handler in Express to return `res.status(200).send('OK')`.

### BUG-002: Authentication Rejection Returns HTTP 200 OK
- **Endpoint**: `POST /auth`
- **Expected Behavior**: HTTP `401 Unauthorized` with structured error body when bad credentials are supplied.
- **Observed Behavior**: HTTP `200 OK` with body `{"reason": "Bad credentials"}`.
- **Classification**: Target API Defect (Anti-pattern).
- **Remediation**: Return `res.status(401).json({ error: "Invalid credentials" })`.

### BUG-003: Missing Required Fields Trigger Unhandled 500 Internal Server Error
- **Endpoint**: `POST /booking`
- **Expected Behavior**: HTTP `400 Bad Request` or `422 Unprocessable Entity` identifying missing mandatory fields.
- **Observed Behavior**: HTTP `500 Internal Server Error`.
- **Classification**: Target API Defect (Unhandled Exception).
- **Remediation**: Add schema validation middleware (e.g. Joi or Zod) to validate request body before hitting the repository layer.

### BUG-004: Explicit Null Values in Required Fields Trigger 500 Error
- **Endpoint**: `POST /booking` (Payload: `{"firstname": null, ...}`)
- **Expected Behavior**: HTTP `400 Bad Request`.
- **Observed Behavior**: HTTP `500 Internal Server Error`.
- **Classification**: Target API Defect.

### BUG-005: Resource Deletion Returns HTTP 201 Created
- **Endpoint**: `DELETE /booking/{id}`
- **Expected Behavior**: HTTP `200 OK` or `204 No Content`.
- **Observed Behavior**: HTTP `201 Created` with body `"Created"`.
- **Classification**: Target API Defect.

### BUG-006: Repeated Deletion Returns 405 Method Not Allowed
- **Endpoint**: `DELETE /booking/{id}` (called after resource is deleted)
- **Expected Behavior**: HTTP `404 Not Found` (or `204 No Content` for idempotent delete semantics).
- **Observed Behavior**: HTTP `405 Method Not Allowed`.
- **Classification**: Target API Defect / Router Misconfiguration.
- **Remediation**: Express route matching fails to locate the resource record and defaults to the router's fall-through handler.

### BUG-007: Decimal Identifier Truncation via `parseInt()`
- **Endpoint**: `GET /booking/12.34`
- **Expected Behavior**: HTTP `400 Bad Request` or `404 Not Found`.
- **Observed Behavior**: HTTP `200 OK` returning booking ID `12`.
- **Classification**: Target API Defect (Loose Type Coercion).
- **Root Cause**: `parseInt(req.params.id, 10)` truncates characters following the period.
- **Remediation**: Validate parameter with integer regex `^\d+$` before parsing.

### BUG-008: Checkin Query Filter Uses Strict Inequality
- **Endpoint**: `GET /booking?checkin=YYYY-MM-DD`
- **Expected Behavior**: Match records where `booking.checkin >= query.checkin`.
- **Observed Behavior**: Matches records where `booking.checkin > query.checkin` (strictly greater than).
- **Classification**: Target API Defect.

### BUG-009: Negative Booking Prices Accepted
- **Endpoint**: `POST /booking` (Payload: `{"totalprice": -500, ...}`)
- **Expected Behavior**: HTTP `400 Bad Request` enforcing `totalprice >= 0`.
- **Observed Behavior**: HTTP `200 OK` storing negative price.
- **Classification**: Business Logic Validation Defect.

### BUG-010: Chronologically Reversed Dates Accepted
- **Endpoint**: `POST /booking` (Payload: `{"checkin": "2026-05-10", "checkout": "2026-05-01"}`)
- **Expected Behavior**: HTTP `400 Bad Request` validating `checkout >= checkin`.
- **Observed Behavior**: HTTP `200 OK` storing reversed dates without error.
- **Classification**: Business Logic Validation Defect.

---

## 2. Platform & Architectural Limitations

### LIMITATION-001: Lack of Pagination Support
- Restful-Booker does not implement pagination (`limit`, `offset`, `cursor`). All `GET /booking` calls return the entire collection, which can exceed 1,500 records on the public demo instance.
- **Future Adaptation**: In enterprise APIs, the framework's `BookingClient` can accept pagination parameters and return structured page envelopes.

### LIMITATION-002: Lack of Sorting Support
- Query parameters such as `?sort=firstname&order=asc` are ignored.

### LIMITATION-003: Shared State and Automatic Periodic Data Resets
- Because Restful-Booker runs as a shared public demo service, the database is periodically reset by a scheduled worker.
- **Framework Isolation Mitigation**: Every test dynamically creates its own resources, executes immediately, and cleans up via `ResourceTracker`. No test relies on pre-existing records or fixed IDs.
