"""Expense: money going out."""
from __future__ import annotations

from typing import Any

from models.transaction import Transaction


class Expense(Transaction):
    def __init__(self, id: int, amount: float, date: str, category: str,
                 note: str = "", payment_method: str = "cash") -> None:
        super().__init__(id, amount, date, category, note)  # category is required by the parent
        self._payment_method: str = str(payment_method).strip() or "cash"

    @property
    def payment_method(self) -> str:
        return self._payment_method

    def signed_amount(self) -> float:
        return -self.amount  # money out: negative

    def label(self) -> str:
        return "Expense"

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["payment_method"] = self._payment_method
        return data
