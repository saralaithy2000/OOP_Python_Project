"""Budget: a monthly spending limit for one category."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from exceptions import ValidationError
from models.expense import Expense
from models.transaction import Transaction


class Budget:
    def __init__(self, category: str, limit: float, month: str) -> None:
        if not isinstance(category, str) or not category.strip():
            raise ValidationError("Budget category is required")
        self._category: str = category.strip()
        self.limit = limit
        self.month = month

    @property
    def category(self) -> str:
        return self._category

    @property
    def limit(self) -> float:
        return self._limit

    @limit.setter
    def limit(self, value: float) -> None:
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValidationError("Budget limit must be a number") from None
        if not math.isfinite(number) or number < 0:
            raise ValidationError("Budget limit cannot be negative")
        self._limit: float = round(number, 2)

    @property
    def month(self) -> str:
        return self._month

    @month.setter
    def month(self, value: str) -> None:
        try:
            parsed = datetime.strptime(str(value), "%Y-%m")
        except ValueError:
            raise ValidationError("Month must be in the format YYYY-MM") from None
        if parsed.strftime("%Y-%m") != value:
            raise ValidationError("Month must be in the format YYYY-MM")
        self._month: str = value

    def spent(self, transactions: list[Transaction]) -> float:
        """Total of the expenses in this budget's category and month."""
        total = 0.0
        for tx in transactions:
            if (isinstance(tx, Expense) and tx.category == self._category
                    and tx.date.startswith(self._month)):
                total += tx.amount
        return round(total, 2)

    def remaining(self, transactions: list[Transaction]) -> float:
        return round(self._limit - self.spent(transactions), 2)

    def is_exceeded(self, transactions: list[Transaction]) -> bool:
        return self.spent(transactions) > self._limit

    def to_dict(self) -> dict[str, Any]:
        return {"category": self._category, "limit": self._limit, "month": self._month}

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Budget:
        try:
            return Budget(data["category"], data["limit"], data["month"])
        except KeyError as error:
            raise ValidationError(f"Budget record is missing the field {error}") from None
