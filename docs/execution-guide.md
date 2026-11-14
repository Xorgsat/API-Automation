# Framework Execution Guide

## 1. Quick Start

### 1.1 Prerequisites
- Python 3.10+ (tested on Python 3.12.16)
- Node.js 18+ & npm (for complementary TypeScript suite)
- `uv` (recommended) or standard `venv` + `pip`

### 1.2 Virtual Environment & Dependency Installation

Using `uv`:
```bash
# Create Python 3.12 virtual environment
uv venv --python 3.12 .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies in editable mode with development tools
uv pip install -e ".[dev]"
```

Using standard `pip`:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 2. Pre-Flight Environment Validation

Before executing the full test battery, verify target API connectivity:
```bash
python scripts/check_environment.py
```
Expected output:
```text
=== Environment Pre-Flight Check: [DEV] ===
Base URL: https://restful-booker.herokuapp.com
Configured Timeout: 15.0s
1. Checking service health (/ping)... SUCCESS [HTTP 201] (Latency: 0.692s)
2. Checking admin authentication (/auth)... SUCCESS [HTTP 200] (Token acquired: 723b***70bd)
3. Checking booking collection access (/booking)... SUCCESS [HTTP 200] (Total bookings visible: 1333)

✓ Environment is ONLINE, responsive, and ready for test automation.
```

---

## 3. Test Execution Profiles

### 3.1 Smoke Tests (Health & Core Availability)
```bash
# Via script
python scripts/run_smoke.py

# Or via pytest marker
pytest -m smoke -v --html=reports/smoke-report.html --self-contained-html
```

### 3.2 Category-Specific Execution

| Test Category | Pytest Command |
|---|---|
| **Functional CRUD** | `pytest -m functional -v` |
| **Authentication** | `pytest -m authentication -v` |
| **Authorization** | `pytest -m security -v` |
| **Negative Testing** | `pytest -m negative -v` |
| **Boundary Analysis** | `pytest -m boundary -v` |
| **API Contracts** | `pytest -m contract -v` |
| **HTTP Semantics** | `pytest -m idempotency -v` |
| **Concurrency** | `pytest -m concurrency -v` |
| **Performance** | `pytest -m performance -v` |

### 3.3 Full Sequential Regression Suite
```bash
python scripts/run_regression.py
```

### 3.4 Full Parallel Regression Suite (pytest-xdist)
```bash
# Run with 4 parallel worker processes
python scripts/run_regression.py --parallel --workers 4

# Or run with auto-detected CPU cores
pytest -n auto -v --html=reports/parallel-report.html --self-contained-html
```

---

## 4. Complementary Playwright TypeScript Suite

To run the cross-language Playwright API parity suite:

```bash
cd playwright-api
npm install
npx playwright test
```

Inspect HTML Playwright report:
```bash
npx playwright show-report
```

---

## 5. Report Inspection

All reports are saved directly to the `reports/` directory:
- `reports/regression-report.html`: Self-contained interactive HTML report with diagnostics, duration metrics, and test logs.
- `reports/junit.xml`: Machine-readable JUnit XML for CI/CD test dashboards.
- `reports/smoke-report.html`: Smoke test execution report.
- `playwright-api/playwright-report/`: Playwright HTML report.
