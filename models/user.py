"""User: the person using the app; owns accounts (composition)."""
from __future__ import annotations

from exceptions import NotFoundError, ValidationError
from models.account import Account


class User:
    def __init__(self, name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("User name is required")
        self._name: str = name.strip()
        self._accounts: list[Account] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def accounts(self) -> list[Account]:
        return list(self._accounts)

    def add_account(self, account: Account) -> None:
        if any(a.name == account.name for a in self._accounts):
            raise ValidationError(f"An account named {account.name!r} already exists")
        self._accounts.append(account)

    def get_account(self, name: str) -> Account:
        for account in self._accounts:
            if account.name == name:
                return account
        raise NotFoundError(f"No account named {name!r}")
