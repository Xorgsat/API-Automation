# Troubleshooting and Operational Diagnostics

## 1. Common Operational Scenarios

### 1.1 Heroku Dyno Cold Starts & Initial Request Latency
- **Symptom**: The first test (typically `/ping` or `/auth`) takes 10 to 15 seconds, while subsequent requests take ~200ms.
- **Root Cause**: Restful-Booker runs on a Heroku free/hobby dyno that sleeps after periods of inactivity. Waking the container requires spinning up Node.js and the Express application.
- **Framework Mitigation**: The default HTTP timeout is configured to `15.0s` (`API_TIMEOUT=15.0`) in `config/environments/dev.yaml`. If connecting to a sleeping instance, the client accommodates the spin-up without crashing.

### 1.2 Multi-Worker Race Conditions & Concurrency
- **Symptom**: Two tests attempting to modify the same resource simultaneously.
- **Framework Mitigation**: The framework implements strict **Resource Isolation**. Every test provisions its own uniquely tagged entities using `BookingFactory` (e.g. `Auto_Alice_x89a`). Tests never share booking IDs across workers or test files.

### 1.3 Database Reset Interruption
- **Symptom**: A resource created a second ago suddenly returns `404 Not Found`.
- **Root Cause**: Restful-Booker periodically executes a background worker that resets the database back to default seed records.
- **Framework Mitigation**: `ResourceTracker` safely tolerates `404` and `405` responses during teardowns. If a database reset occurs during teardown, the tracker records a warning without failing the test run or masking the primary test assertion.

### 1.4 Correlation ID Tracing
- Every outgoing request is assigned a unique `X-Correlation-ID` header.
- If a request fails, the failure diagnostics print the correlation ID, request method, full URL, request headers, payload preview, response status, response headers, and response body preview.
- Search test logs using the correlation ID to reconstruct the exact HTTP transaction.

---

## 2. Playwright TypeScript Suite Troubleshooting

### "playwright: command not found" or "Cannot find module '@playwright/test'"
Ensure dependencies were installed inside the `playwright-api/` directory:
```bash
cd playwright-api
npm install
npx playwright test
```

### Changing Target Base URL for Playwright
Pass the environment variable during invocation:
```bash
API_BASE_URL="https://my-staging-api.com" npx playwright test
```
