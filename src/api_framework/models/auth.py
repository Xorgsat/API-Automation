"""Pydantic models for authentication payloads and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuthRequest(BaseModel):
    """Payload model for POST /auth."""

    model_config = ConfigDict(extra="forbid")

    username: str = Field(..., description="Administrator username")
    password: str = Field(..., description="Administrator password")

    def to_dict(self) -> dict[str, Any]:
        """Serialize payload to dict."""
        return self.model_dump()


class AuthSuccessResponse(BaseModel):
    """Response returned upon successful authentication."""

    model_config = ConfigDict(extra="ignore")

    token: str = Field(..., description="Session authentication token")


class AuthFailureResponse(BaseModel):
    """Response returned when authentication fails with invalid credentials."""

    model_config = ConfigDict(extra="ignore")

    reason: str = Field(default="Bad credentials", description="Failure reason")
