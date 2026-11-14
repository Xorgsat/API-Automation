# System Architecture & Technical Design

## 1. Architectural Philosophy

The **API Quality Engineering Framework** is architected according to clean architectural separation of concerns:
- **Maintainability over premature abstraction**: Direct, clear Python abstractions without deep class hierarchies.
- **Transport vs. Business vs. Assertions**: HTTP details are completely decoupled from domain operations, and assertions remain strictly in the test and assertion layers.
- **Strict Test Isolation**: Tests never share mutable state or depend on execution ordering.
- **Comprehensive Diagnostics**: Outgoing requests and incoming responses are intercepted, timed, sanitized, and logged with unique correlation IDs.

---

## 2. High-Level Component Architecture

```mermaid
graph TD
    subgraph Test_Layer [Test Execution Layer]
        SmokeTests[Smoke Tests]
        FuncTests[Functional CRUD Tests]
        NegTests[Negative & Boundary Tests]
        ContractTests[Contract & Schema Tests]
        SecurityTests[Security & Auth Tests]
        PerfTests[Performance Measurements]
    end

    subgraph Service_Layer [Service Abstraction Layer]
        BookingService[BookingService]
        AuthService[AuthService]
        HealthService[HealthService]
    end

    subgraph Client_Layer [HTTP Transport Client Layer]
        BookingClient[BookingClient]
        AuthClient[AuthClient]
        HealthClient[HealthClient]
        BaseClient[BaseAPIClient requests.Session]
    end

    subgraph Core_Support [Core Cross-Cutting Components]
        Config[Settings & YAML Profiles]
        AuthMgr[AuthManager & Token Cache]
        Factory[BookingFactory & RandomData]
        SchemaVal[JSON Schema Draft-07 Registry]
        PydanticModels[Pydantic V2 Models]
        Assertions[Response & Domain Assertions]
        ResourceTracker[ResourceTracker Teardown Registry]
    end

    Test_Layer --> Service_Layer
    Test_Layer --> Assertions
    Test_Layer --> SchemaVal
    Test_Layer --> Factory
    Test_Layer --> ResourceTracker

    Service_Layer --> Client_Layer
    Service_Layer --> PydanticModels

    Client_Layer --> BaseClient
    Client_Layer --> AuthMgr
    BaseClient --> Config
```

---

## 3. Request Execution Flow

Every HTTP request traverses a structured lifecycle:

```mermaid
sequenceDiagram
    autonumber
    participant Test as Test Case
    participant Service as BookingService
    participant Client as BookingClient
    participant Transport as BaseAPIClient
    participant API as Restful-Booker API

    Test->>Service: create_booking(payload)
    Service->>Client: create_booking(payload, headers)
    Client->>Transport: post("/booking", json_data, headers)
    Note over Transport: Generate Correlation ID<br/>Sanitize Headers & Body<br/>Start High-Resolution Timer
    Transport->>API: HTTP POST /booking
    API-->>Transport: HTTP Response (200 OK)
    Note over Transport: Record Elapsed Seconds<br/>Attach Correlation ID<br/>Log Response Preview
    Transport-->>Client: requests.Response
    Client-->>Service: requests.Response
    Service->>Service: Deserialize to Pydantic CreateBookingResponse
    Service-->>Test: (Response, CreateBookingResponse)
    Test->>Test: assert_status_code(200)<br/>validate_schema("booking_response.schema.json")
```

---

## 4. Authentication Flow

Restful-Booker utilizes session token cookies for mutating requests (`PUT`, `PATCH`, `DELETE`) with an HTTP Basic Authentication alternative:

```mermaid
sequenceDiagram
    autonumber
    participant Test as Test Case
    participant AuthMgr as AuthManager
    participant AuthClient as AuthClient
    participant BookingClient as BookingClient
    participant API as Restful-Booker API

    Test->>AuthMgr: get_cookie_header()
    alt Token not in Cache or Forced Refresh
        AuthMgr->>AuthClient: create_token(username, password)
        AuthClient->>API: POST /auth {username, password}
        API-->>AuthClient: 200 OK {"token": "723b...70bd"}
        AuthClient-->>AuthMgr: requests.Response
        AuthMgr->>AuthMgr: Cache Token in Thread-Safe Registry
    end
    AuthMgr-->>Test: {"Cookie": "token=723b...70bd"}
    Test->>BookingClient: update_booking(id, payload, token)
    BookingClient->>API: PUT /booking/{id} [Cookie: token=...]
    API-->>BookingClient: 200 OK {updated_booking}
```

---

## 5. Test Data Lifecycle & Isolation

To guarantee deterministic test execution against a public shared API with automatic data resets:

```mermaid
sequenceDiagram
    autonumber
    participant Pytest as Pytest Runner
    participant Fixture as created_booking Fixture
    participant Tracker as ResourceTracker
    participant Factory as BookingFactory
    participant Service as BookingService
    participant Test as Test Execution
    participant API as Restful-Booker API

    Pytest->>Fixture: Setup created_booking
    Fixture->>Factory: build_valid() -> unique randomized data
    Fixture->>Service: create_booking(payload)
    Service->>API: POST /booking
    API-->>Service: 200 OK {"bookingid": 3105, ...}
    Fixture->>Tracker: register("Booking 3105", cleanup_callback)
    Fixture-->>Test: Yield (booking_id=3105, payload)
    
    Note over Test: Execute Test Assertions<br/>Isolated from Other Tests
    
    Test-->>Pytest: Test Completed
    Pytest->>Tracker: run_cleanups()
    Tracker->>Service: delete_booking(3105, token)
    Service->>API: DELETE /booking/3105
    API-->>Service: 201 Created (Deleted)
    Note over Tracker: Cleanup exceptions caught & logged<br/>Original test status preserved
```

---

## 6. Technology Justification Matrix

| Technology | Purpose | Justification |
|---|---|---|
| **Python 3.12** | Core Language | Expressive, industry-standard language with rich quality engineering ecosystem. |
| **pytest 8+** | Test Framework | Mature fixture system, parametrized test execution, xdist parallelization, and clean assertions. |
| **requests** | HTTP Transport | Predictable, stable, well-understood transport with explicit connection pooling and adapter configuration. |
| **Pydantic V2** | Data Modeling | Strict schema validation, fast parsing, and separation between request objects and response structures. |
| **jsonschema** | Contract Testing | Independent JSON Schema Draft-07 specification validation, decoupling contracts from Python implementation details. |
| **pytest-xdist** | Concurrency | Multi-process worker distribution for high-throughput parallel test execution. |
| **pytest-html** | Reporting | Self-contained, portable HTML execution reports for stakeholder review and CI artifact archiving. |
| **Playwright (TS)** | Cross-Language Parity | Demonstrates multi-language API automation capabilities using modern TypeScript `APIRequestContext`. |
