"""Abstract base class shared by Income and Expense."""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from exceptions import ValidationError


class Transaction(ABC):
    """A movement of money. Cannot be created directly: use Income or Expense."""

    def __init__(self, id: int, amount: float, date: str, category: str, note: str = "") -> None:
        if not isinstance(id, int) or id <= 0:
            raise ValidationError("ID must be a positive whole number")
        self._id: int = id
        # Assign through the properties (not self._amount) so the setters validate the values.
        self.amount = amount
        self.date = date
        self.category = category
        self.note = note

    # ---------- properties (controlled access to private data) ----------
    @property
    def id(self) -> int:
        return self._id  # read-only: there is no setter

    @property
    def amount(self) -> float:
        return self._amount

    @amount.setter
    def amount(self, value: float) -> None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Amount must be a number") from None
        if not math.isfinite(number) or number <= 0:
            raise ValidationError("Amount must be greater than zero")
        self._amount: float = round(number, 2)

    @property
    def date(self) -> str:
        return self._date

    @date.setter
    def date(self, value: str) -> None:
        try:
            parsed = datetime.strptime(str(value), "%Y-%m-%d")
        except ValueError:
            raise ValidationError("Date must be a real date in the format YYYY-MM-DD") from None
        if parsed.strftime("%Y-%m-%d") != value:  # rejects forms like 2026-1-5
            raise ValidationError("Date must be in the format YYYY-MM-DD")
        self._date: str = value

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Category is required")
        self._category: str = value.strip()

    @property
    def note(self) -> str:
        return self._note

    @note.setter
    def note(self, value: str) -> None:
        self._note: str = str(value).strip()

    # ---------- abstract methods: every child MUST implement these ----------
    @abstractmethod
    def signed_amount(self) -> float:
        """Amount with its sign: positive for income, negative for expense."""

    @abstractmethod
    def label(self) -> str:
        """Text shown in the GUI: 'Income' or 'Expense'."""

    # ---------- saving and loading ----------
    def to_dict(self) -> dict[str, Any]:
        """Convert this object to a plain dictionary that JSON can store."""
        return {
            "id": self._id,
            "type": self.label().lower(),
            "amount": self._amount,
            "date": self._date,
            "category": self._category,
            "note": self._note,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Transaction:
        """Build an Income or an Expense from a dictionary (factory method)."""
        # Imported here, not at the top, to avoid a circular import (the children import this file).
        from models.expense import Expense
        from models.income import Income

        try:
            kind = data["type"]
            common = dict(id=data["id"], amount=data["amount"], date=data["date"],
                          category=data["category"], note=data.get("note", ""))
        except KeyError as error:
            raise ValidationError(f"Transaction record is missing the field {error}") from None
        if kind == "income":
            return Income(**common, source=data.get("source", ""))
        if kind == "expense":
            return Expense(**common, payment_method=data.get("payment_method", "cash"))
        raise ValidationError(f"Unknown transaction type: {kind!r}")

    def __repr__(self) -> str:
        return f"{self.label()}(id={self._id}, amount={self._amount}, date={self._date}, category={self._category})"
