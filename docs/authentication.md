# Authentication and Authorization Architecture

## 1. Overview

This document details the authentication and authorization mechanisms utilized by **Restful-Booker**, how the automation framework handles credential security and token lifecycles, and how authorization enforcement is validated.

---

## 2. Authentication Protocol Analysis

### 2.1 The Token Exchange
- **Endpoint**: `POST /auth`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "username": "admin",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "token": "723bf275fca65ad"
  }
  ```

### 2.2 Critical Distinction: Opaque Token vs. JWT
A common misconception in test automation suites is assuming this token is a JSON Web Token (JWT).
Our framework performs an explicit structural check (`tests/authentication/test_authentication.py`):
1. **Opaque Token**: Restful-Booker generates a 15-character hexadecimal/alphanumeric random string.
2. **Not a JWT**: It does **not** contain three Base64URL-encoded parts (`header.payload.signature`) separated by dots, nor does it contain expiration claims (`exp`) or cryptographic signatures.

---

## 3. Authorization Mechanisms

Restful-Booker supports two distinct authorization mechanisms for mutating requests (`PUT`, `PATCH`, `DELETE`):

### 3.1 Cookie-Based Token Authentication (Primary)
The client includes the session token in the `Cookie` HTTP header:
```http
PUT /booking/123 HTTP/1.1
Host: restful-booker.herokuapp.com
Cookie: token=723bf275fca65ad
Content-Type: application/json
```

### 3.2 HTTP Basic Authentication (Secondary)
The client includes the Base64-encoded credentials in the `Authorization` header:
```http
DELETE /booking/123 HTTP/1.1
Host: restful-booker.herokuapp.com
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

---

## 4. Framework Security & Credential Hygiene

### 4.1 No Hardcoded Secrets
Credentials are never hardcoded inside test scripts. They are resolved via:
1. `API_AUTH_USERNAME` and `API_AUTH_PASSWORD` environment variables.
2. YAML environment configuration profiles (`config/environments/dev.yaml`).
3. GitHub Secrets in CI/CD workflows.

### 4.2 Automated Secret Masking in Logs
The framework implements automated sanitization (`api_framework.utils.sanitization`):
- Any header named `Cookie`, `Authorization`, or `Token` has its sensitive token value masked (e.g. `token=723b***65ad`).
- Any JSON payload key named `password`, `token`, or `secret` is replaced with `***` prior to emitting log messages or report attachments.

---

## 5. Authorization Verification Matrix

| Endpoint | Method | Without Auth | Invalid Token | Invalid Basic Auth | Valid Token / Auth |
|---|---|---|---|---|---|
| `/booking` | POST | 200 OK (Public) | 200 OK | 200 OK | 200 OK |
| `/booking/{id}` | GET | 200 OK (Public) | 200 OK | 200 OK | 200 OK |
| `/booking/{id}` | PUT | 403 Forbidden | 403 Forbidden | 403 Forbidden | 200 OK |
| `/booking/{id}` | PATCH | 403 Forbidden | 403 Forbidden | 403 Forbidden | 200 OK |
| `/booking/{id}` | DELETE | 403 Forbidden | 403 Forbidden | 403 Forbidden | 201 Created |
