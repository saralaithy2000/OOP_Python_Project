"""Account: owns a list of transactions (composition)."""
from __future__ import annotations

import math

from exceptions import NotFoundError, ValidationError
from models.transaction import Transaction


class Account:
    def __init__(self, name: str, opening_balance: float = 0.0) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Account name is required")
        try:
            balance = float(opening_balance)
        except (TypeError, ValueError):
            raise ValidationError("Opening balance must be a number") from None
        if not math.isfinite(balance):
            raise ValidationError("Opening balance must be a number")
        self._name: str = name.strip()
        self._opening_balance: float = balance
        self._transactions: list[Transaction] = []  # the Account HAS transactions

    @property
    def name(self) -> str:
        return self._name

    @property
    def opening_balance(self) -> float:
        return self._opening_balance

    @property
    def transactions(self) -> list[Transaction]:
        return list(self._transactions)  # a COPY, so outside code cannot bypass our checks

    def add_transaction(self, tx: Transaction) -> None:
        if any(existing.id == tx.id for existing in self._transactions):
            raise ValidationError(f"A transaction with ID {tx.id} already exists")
        self._transactions.append(tx)

    def find_by_id(self, tx_id: int) -> Transaction:
        for tx in self._transactions:
            if tx.id == tx_id:
                return tx
        raise NotFoundError(f"No transaction with ID {tx_id}")

    def remove_transaction(self, tx_id: int) -> None:
        tx = self.find_by_id(tx_id)  # raises NotFoundError if missing
        self._transactions.remove(tx)

    def balance(self) -> float:
        # Polymorphism: each object reports its own sign, no if/else needed.
        return round(self._opening_balance + sum(tx.signed_amount() for tx in self._transactions), 2)
