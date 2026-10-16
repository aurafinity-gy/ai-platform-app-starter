"""Pure domain rules: no framework or persistence dependencies."""
from dataclasses import dataclass


class InvalidTitle(ValueError):
    pass


def validate_title(value: str) -> str:
    title = value.strip()
    if not 1 <= len(title) <= 120:
        raise InvalidTitle("Title must contain 1–120 non-space characters")
    return title


@dataclass(frozen=True)
class Item:
    id: str
    tenant_id: str
    title: str
    revision: int
