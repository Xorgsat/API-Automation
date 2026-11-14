"""JSON Schema validation module.

Loads, manages, and executes JSON Schema Draft-07 validation against API responses
independently of Pydantic models.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, ValidationError
from referencing import Registry, Resource

SCHEMA_DIR = Path(__file__).resolve().parent


def load_json_schema(filename: str) -> dict[str, Any]:
    """Load a schema dictionary from the schemas directory."""
    path = SCHEMA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# Build shared registry for cross-schema references
_BOOKING_SCHEMA = load_json_schema("booking.schema.json")
_REGISTRY: Registry = Registry().with_resource(
    uri="booking.schema.json",
    resource=Resource.from_contents(_BOOKING_SCHEMA),
)


def get_validator(schema_name: str) -> Draft7Validator:
    """Return a compiled Draft7Validator for the named schema."""
    schema = load_json_schema(schema_name)
    return Draft7Validator(schema, registry=_REGISTRY)


def validate_schema(data: Any, schema_name: str) -> None:
    """Validate JSON data against a named schema file.

    Raises jsonschema.ValidationError with detailed diagnostic message if non-compliant.
    """
    validator = get_validator(schema_name)
    validator.validate(data)


__all__ = [
    "ValidationError",
    "get_validator",
    "load_json_schema",
    "validate_schema",
]
