"""Income: money coming in."""
from __future__ import annotations

from typing import Any

from models.transaction import Transaction


class Income(Transaction):
    def __init__(self, id: int, amount: float, date: str, category: str,
                 note: str = "", source: str = "") -> None:
        super().__init__(id, amount, date, category, note)  # parent stores the shared fields
        self._source: str = str(source).strip()               # data only Income has

    @property
    def source(self) -> str:
        return self._source

    def signed_amount(self) -> float:
        return self.amount  # money in: positive

    def label(self) -> str:
        return "Income"

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()      # start from the parent's dictionary...
        data["source"] = self._source  # ...and add what is specific to Income
        return data
