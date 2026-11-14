# Comprehensive API Test Strategy

## 1. Test Strategy Overview

The **API Quality Engineering Framework** employs a risk-based, layered testing strategy designed to provide rapid feedback, high defect detection, contract stability, and repeatable execution against RESTful services.

---

## 2. Test Classification Matrix

| Category | Marker | Objective | Minimum Target | Executed Count | Focus Areas |
|---|---|---|---|---|---|
| **Smoke** | `@pytest.mark.smoke` | Verify basic service uptime, `/ping` availability, and foundational readiness | 4 | 4 | Health check status, latency SLA, Content-Type, unallowed methods |
| **Functional CRUD** | `@pytest.mark.functional` | Validate complete business workflows for Create, Read, Update, Delete, and Query filters | 42 | 44 | Full creation, read-after-write, PUT/PATCH updates, Basic Auth updates, deletion verification |
| **Authentication** | `@pytest.mark.authentication` | Verify credential exchange, token generation, and rejection behaviors | 12 | 12 | Valid credentials, bad username/password, empty payloads, opaque token format vs JWT |
| **Authorization** | `@pytest.mark.security` | Enforce access control on mutating endpoints | 10 | 10 | Unauthenticated PUT/PATCH/DELETE, invalid tokens, invalid Basic Auth, information leakage |
| **Negative Testing** | `@pytest.mark.negative` | Verify system resilience against malformed inputs and invalid states | 20 | 25 | Malformed JSON, missing required fields, nulls, array root, bad headers, unsupported methods |
| **Boundary Analysis** | `@pytest.mark.boundary` | Validate extreme parameter boundaries | 20 | 20 | Price limits (0, negative, max int), string lengths (1 to 1000 chars), Unicode, leap years |
| **API Contracts** | `@pytest.mark.contract` | Validate strict conformance to JSON Schema Draft-07 contracts | 12 | 12 | Schema validation across all endpoints, missing property rejection, type checks |
| **HTTP Semantics** | `@pytest.mark.idempotency` | Verify RFC 9110 HTTP method semantics | 6 | 6 | Safe GET, idempotent PUT, non-idempotent POST, DELETE repeat behavior |
| **Concurrency** | `@pytest.mark.concurrency` | Validate thread safety, resource isolation, and race-condition prevention | 5 | 5 | Parallel creation, parallel reads, parallel independent updates, parallel auth |
| **Performance** | `@pytest.mark.performance` | Measure lightweight API response latency profiles against SLAs | 4 | 4 | Latency percentiles (min, max, mean, median, p95), failure rate monitoring |

---

## 3. Test Design Techniques Applied

### 3.1 Equivalence Partitioning (EP)
- **Guest Names**: Valid alphabet strings vs empty strings vs numeric types vs null.
- **Total Price**: Positive integer range $[1, 2^{31}-1]$ vs zero vs negative values vs non-numeric string values.
- **Deposit Paid**: Boolean `true` / `false` vs string representations vs numbers.
- **Dates**: Standard ISO formats (`YYYY-MM-DD`) vs non-ISO strings vs empty strings vs inverted ranges.

### 3.2 Boundary Value Analysis (BVA)
- **Numeric Limits**: Minimum valid price ($0, $1), negative values ($-1, $-9999), and upper limit ($2,147,483,647$).
- **String Lengths**: 1 character (minimum boundary), 255 characters (standard varchar), 1,000 characters (stress boundary).
- **Date Boundaries**: Same-day checkin/checkout ($0$-night stay), leap year day (`2028-02-29`), and distant future dates (`2099-12-31`).

### 3.3 State Transition Testing
- Booking lifecycle transitions:
  $$\text{Non-Existent} \xrightarrow{\text{POST}} \text{Created} \xrightarrow{\text{GET}} \text{Verified} \xrightarrow{\text{PUT/PATCH}} \text{Updated} \xrightarrow{\text{DELETE}} \text{Deleted (404)}$$
- Repeated deletion transition:
  $$\text{Deleted} \xrightarrow{\text{DELETE}} \text{Method Not Allowed (405)}$$

### 3.4 Negative Testing & Defect Discovery
- Injection of unclosed JSON structures (`"{bad`).
- Omission of each required property individually (`firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates`).
- Omission of Content-Type headers and submission of unsupported media types.

---

## 4. Test Isolation Strategy

1. **Unique Data Generation**: Every test generates distinct, timestamped/randomized strings for `firstname` and `lastname` to prevent collisions.
2. **Dynamic Creation & Ephemeral Lifecycles**: Tests create fresh resources on demand and avoid depending on hardcoded IDs (e.g. ID `1` or `2`).
3. **Resilient Teardown with `ResourceTracker`**: Created booking IDs are registered in the tracker fixture and deleted during teardown. Cleanup errors (e.g. if the test already deleted the booking) are safely trapped and logged without failing the test suite or masking original test failures.
