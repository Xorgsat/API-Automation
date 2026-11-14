"""Authentication test suite evaluating /auth endpoint, credentials, and token structures."""

from __future__ import annotations

import pytest

from api_framework.assertions.response_assertions import (
    assert_content_type,
    assert_response_time_less_than,
    assert_status_code,
)
from api_framework.models.auth import AuthFailureResponse, AuthSuccessResponse
from api_framework.services.auth_service import AuthService
from config.settings import Settings


@pytest.mark.authentication
class TestAuthentication:
    """Validate authentication flows, credential checks, and token generation."""

    def test_auth_valid_credentials_generates_token(
        self,
        auth_service: AuthService,
        settings: Settings,
    ) -> None:
        """Verify valid admin credentials return HTTP 200 and a token string."""
        resp, parsed = auth_service.authenticate(
            username=settings.auth.username,
            password=settings.auth.password,
        )

        assert_status_code(resp, 200)
        assert_content_type(resp, "application/json")
        assert_response_time_less_than(resp, 5.0)

        assert parsed is not None
        assert isinstance(parsed, AuthSuccessResponse)
        assert len(parsed.token) > 0

    def test_token_structure_is_opaque_token_not_jwt(
        self,
        auth_service: AuthService,
        settings: Settings,
    ) -> None:
        """Verify token is an opaque hexadecimal/alphanumeric string, NOT a JSON Web Token (JWT).

        A JWT consists of 3 Base64URL-encoded parts separated by dots (header.payload.signature).
        Restful-Booker generates 15-character opaque tokens.
        """
        _, parsed = auth_service.authenticate(
            username=settings.auth.username,
            password=settings.auth.password,
        )
        assert isinstance(parsed, AuthSuccessResponse)
        token = parsed.token
        parts = token.split(".")
        # Confirm it does not conform to JWT structure
        assert len(parts) != 3, f"Token was unexpectedly in JWT format: {token}"
        assert len(token) >= 10, f"Token length unexpectedly short: {len(token)}"

    @pytest.mark.parametrize(
        ("username", "password", "test_id"),
        [
            ("invalid_user", "password123", "invalid_username"),
            ("admin", "wrong_password", "invalid_password"),
            ("unknown", "unknown", "both_invalid"),
            ("", "password123", "empty_username"),
            ("admin", "", "empty_password"),
            ("", "", "both_empty"),
        ],
    )
    def test_auth_invalid_or_empty_credentials(
        self,
        auth_service: AuthService,
        username: str,
        password: str,
        test_id: str,
    ) -> None:
        """Verify invalid or empty credentials return failure response.

        Empirical Note: Restful-Booker returns HTTP 200 OK with {'reason': 'Bad credentials'}
        rather than HTTP 401 Unauthorized.
        """
        resp, parsed = auth_service.authenticate(username=username, password=password)

        assert_status_code(resp, 200)
        assert isinstance(parsed, AuthFailureResponse)
        assert parsed.reason == "Bad credentials"

    def test_auth_missing_fields_payload(self, auth_service: AuthService) -> None:
        """Verify payload with missing required fields returns Bad credentials."""
        resp, parsed = auth_service.authenticate(raw_payload={"username": "admin"})
        assert_status_code(resp, 200)
        assert isinstance(parsed, AuthFailureResponse)
        assert parsed.reason == "Bad credentials"

    def test_auth_empty_json_object(self, auth_service: AuthService) -> None:
        """Verify empty JSON object returns Bad credentials."""
        resp, parsed = auth_service.authenticate(raw_payload={})
        assert_status_code(resp, 200)
        assert isinstance(parsed, AuthFailureResponse)
        assert parsed.reason == "Bad credentials"

    def test_auth_malformed_json_syntax(self, auth_service: AuthService) -> None:
        """Verify malformed JSON body returns HTTP 400 Bad Request."""
        resp, _ = auth_service.authenticate(raw_payload="{invalid-json-structure")
        assert_status_code(resp, 400)
        assert "Bad Request" in resp.text
