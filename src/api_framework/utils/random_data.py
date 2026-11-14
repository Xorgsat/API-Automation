"""Random test data generator for API automation.

Supports controlled, deterministic test data generation with optional seeding
to ensure reproducible test execution and prevent collision during parallel runs.
"""

from __future__ import annotations

import random
import string
import uuid

FIRST_NAMES = [
    "Alex", "Morgan", "Jordan", "Taylor", "Casey", "Riley", "Sam", "Chris", "Pat", "Robin",
    "Avery", "Dakota", "Jamie", "Skyler", "Quinn", "Jesse", "Reese", "Harper", "Rowan", "Hayden"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Anderson",
    "Taylor", "Thomas", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"
]

ADDITIONAL_NEEDS = [
    "Breakfast", "Late Checkout", "Airport Shuttle", "Crib", "Extra Pillows",
    "Quiet Room", "High Floor", "Balcony", "Vegan Meals", "Wheelchair Accessible"
]


class RandomDataGenerator:
    """Configurable random test data generator."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def unique_tag(self, length: int = 8) -> str:
        """Generate a short alphanumeric unique tag."""
        return "".join(self._rng.choices(string.ascii_lowercase + string.digits, k=length))

    def unique_uuid(self) -> str:
        """Generate a unique UUID4 string."""
        return str(uuid.uuid4())

    def first_name(self, prefix: str = "Test") -> str:
        """Generate a randomized first name with unique suffix."""
        base = self._rng.choice(FIRST_NAMES)
        return f"{prefix}_{base}_{self.unique_tag(5)}"

    def last_name(self, prefix: str = "SDET") -> str:
        """Generate a randomized last name with unique suffix."""
        base = self._rng.choice(LAST_NAMES)
        return f"{prefix}_{base}_{self.unique_tag(5)}"

    def total_price(self, min_val: int = 50, max_val: int = 2000) -> int:
        """Generate a realistic booking price."""
        return self._rng.randint(min_val, max_val)

    def deposit_paid(self) -> bool:
        """Generate a boolean deposit status."""
        return self._rng.choice([True, False])

    def additional_needs(self) -> str:
        """Select a realistic additional requirement."""
        return self._rng.choice(ADDITIONAL_NEEDS)

    def string_of_length(self, length: int, chars: str = string.ascii_letters) -> str:
        """Generate a random string of exact length."""
        return "".join(self._rng.choices(chars, k=length))

    def special_character_string(self) -> str:
        """Generate a string containing common symbols and punctuation."""
        return "!@#$%^&*()_+-=[]{}|;':,.<>/?`~"

    def unicode_string(self) -> str:
        """Generate a string with international Unicode characters."""
        return "こんにちは世界_Café_München_Ñandú_🚀"


# Default instance for convenient imports
default_generator = RandomDataGenerator()
