# Target API Analysis & Empirical Discovery

## 1. Executive Summary

This document presents the technical analysis and empirical discovery findings for the **Restful-Booker** REST API (`https://restful-booker.herokuapp.com`), conducted prior to and during framework development.

Rather than relying purely on third-party tutorials or assumptions, every documented endpoint and capability was verified through live HTTP probing against the deployed application.

---

## 2. Documented vs. Verified Endpoint Inventory

| Endpoint | Method | Documented Purpose | Observed HTTP Status | Verified Payload / Content | Verdict |
|---|---|---|---|---|---|
| `/ping` | GET | Health check | `201 Created` | Text: `Created` | Verified Supported (Quirk: 201 instead of 200) |
| `/auth` | POST | Token generation | `200 OK` | `{"token": "<15-char-hex>"}` | Verified Supported |
| `/auth` (bad creds) | POST | Invalid credentials | `200 OK` | `{"reason": "Bad credentials"}` | Verified Defect (200 OK instead of 401) |
| `/booking` | GET | List booking IDs | `200 OK` | `[{"bookingid": <int>}, ...]` | Verified Supported |
| `/booking` | POST | Create booking | `200 OK` | `{"bookingid": <int>, "booking": {...}}` | Verified Supported (200 instead of 201) |
| `/booking/{id}` | GET | Get booking details | `200 OK` | `{"firstname": ..., "bookingdates": {...}}` | Verified Supported |
| `/booking/{id}` | PUT | Full update | `200 OK` | `{"firstname": ..., "bookingdates": {...}}` | Verified Supported (Auth required) |
| `/booking/{id}` | PATCH | Partial update | `200 OK` | `{"firstname": ..., "bookingdates": {...}}` | Verified Supported (Auth required) |
| `/booking/{id}` | DELETE | Delete booking | `201 Created` | Text: `Created` | Verified Supported (Quirk: 201 instead of 204) |
| `/booking/{id}` | DELETE (repeat) | Delete already deleted | `405 Method Not Allowed` | Text: `Method Not Allowed` | Verified Defect (405 instead of 404/204) |

---

## 3. Data Model Deep-Dive

### Booking Entity Attributes

| Field Name | Type | Required | Nullable | Observed Backend Behavior |
|---|---|---|---|---|
| `firstname` | `string` | Yes | No | Omitting causes unhandled 500 error; null value causes 500. Accepts arbitrary string lengths (tested up to 1,000 characters). |
| `lastname` | `string` | Yes | No | Omitting causes 500 error; accepts Unicode and special characters. |
| `totalprice` | `integer` | Yes | No | Accepts 0, negative values (e.g. -500), and large 32-bit signed integers. When passed as a string, stores `null`. |
| `depositpaid` | `boolean` | Yes | No | Accepts `true` / `false`. Coerces string truthiness (e.g. `"yes"` becomes `true`). |
| `bookingdates.checkin` | `string (YYYY-MM-DD)` | Yes | No | ISO date string. Passing empty string stores `"0NaN-aN-aN"` (JavaScript Date parsing artifact). |
| `bookingdates.checkout` | `string (YYYY-MM-DD)` | Yes | No | ISO date string. Does NOT validate that `checkout >= checkin`; permits reversed dates. |
| `additionalneeds` | `string` | No | Yes | Optional field. Accepts emojis, multiline strings, and symbols. |

---

## 4. Query Parameter & Filter Semantics

### Documented Filters
- `firstname`: Query records where `firstname == query_param`.
- `lastname`: Query records where `lastname == query_param`.
- `checkin`: Query records by checkin date.
- `checkout`: Query records by checkout date.

### Empirical Filtering Discoveries

#### 1. Strict Inequality on Checkin Dates
Through controlled testing, we proved that Restful-Booker evaluates:
$$\text{booking.checkin} > \text{query.checkin}$$
*(strictly greater than)* rather than $\ge$. A booking with checkin `2026-05-10` does **not** match `?checkin=2026-05-10`, but **does** match `?checkin=2026-05-09`.

#### 2. Inequality on Checkout Dates
Restful-Booker evaluates:
$$\text{booking.checkout} \le \text{query.checkout}$$

#### 3. Pagination & Sorting: Completely Unsupported
Probing confirmed that parameters like `?limit=5&offset=0` or `?sort=firstname` are completely ignored by the Express backend; the entire unpaginated array of booking objects (1,000+ items) is returned.

---

## 5. Authentication & Authorization Mechanics

1. **Token Nature**: The generated token is a 15-character alphanumeric/hexadecimal string (`[a-f0-9]{15}`). It is **not** a JSON Web Token (JWT) as it lacks the 3 base64url-encoded dot-delimited segments and cryptographic signature.
2. **Cookie Construction**: Authenticated requests must pass the token via HTTP request header:
   ```http
   Cookie: token=<token_value>
   ```
3. **Basic Authentication Fallback**: Supported on mutating endpoints via standard header:
   ```http
   Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
   ```
4. **Authorization Enforcement**:
   - Omitting credentials on `PUT`, `PATCH`, or `DELETE` returns `403 Forbidden` with body `"Forbidden"`.
   - Passing an invalid or expired token returns `403 Forbidden`.
   - Incorrect HTTP Basic Auth credentials return `403 Forbidden`.

---

## 6. Identifier Type Coercion Bug (BUG-007)

When sending `GET /booking/12.34`:
- Expected REST behavior: `400 Bad Request` or `404 Not Found`.
- Observed behavior: `200 OK` returning booking ID `12`.
- Root Cause: Express endpoint implementation uses JavaScript's `parseInt(req.params.id, 10)`, which stops parsing at the decimal point and resolves `12.34` to integer `12`.
