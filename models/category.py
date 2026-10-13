"""Category: a label for transactions, such as Food or Salary."""
from __future__ import annotations

from typing import Any

from exceptions import ValidationError

VALID_KINDS: tuple[str, ...] = ("income", "expense", "both")


class Category:
    def __init__(self, id: int, name: str, kind: str = "both") -> None:
        if not isinstance(id, int) or id <= 0:
            raise ValidationError("Category ID must be a positive whole number")
        self._id: int = id
        self.name = name
        self.kind = kind

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Category name is required")
        self._name: str = value.strip()

    @property
    def kind(self) -> str:
        return self._kind

    @kind.setter
    def kind(self, value: str) -> None:
        if value not in VALID_KINDS:
            raise ValidationError(f"Category kind must be one of {VALID_KINDS}")
        self._kind: str = value

    def to_dict(self) -> dict[str, Any]:
        return {"id": self._id, "name": self._name, "kind": self._kind}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Category:
        try:
            return Category(data["id"], data["name"], data.get("kind", "both"))
        except KeyError as error:
            raise ValidationError(f"Category record is missing the field {error}") from None
