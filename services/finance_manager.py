"""FinanceManager: the service layer between the GUI and the models / files.

Flow:  GUI  ->  FinanceManager  ->  models (Account, Budget, ...) and FileManager
The GUI never touches models or files directly, so every rule lives in one place.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

# NotFoundError is imported here so older code can still do:
#   from services.finance_manager import FinanceManager, NotFoundError
from exceptions import BudgetError, DataFileError, FinanceError, NotFoundError, ValidationError
from file_manager.file_manager import FileManager
from models.account import Account
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from models.income import Income
from models.transaction import Transaction
from models.user import User

EDITABLE_FIELDS: tuple[str, ...] = ("amount", "date", "category", "note", "source", "payment_method")


class FinanceManager:
    def __init__(self, file_manager: FileManager, user_name: str = "User",
                 account_name: str = "Main") -> None:
        self._file_manager: FileManager = file_manager
        self._user_name: str = user_name
        self._account_name: str = account_name
        self._user: User = User(user_name)
        self._account: Account = Account(account_name)
        self._user.add_account(self._account)
        self._categories: list[Category] = []
        self._budgets: list[Budget] = []
        self.load_data()

    # ------------------------------------------------------------------
    # loading and saving
    # ------------------------------------------------------------------
    def load_data(self) -> None:
        """Read everything from the JSON files into objects."""
        account = Account(self._account_name)
        for tx in self._file_manager.load_transactions():
            try:
                account.add_transaction(tx)
            except ValidationError as error:
                raise DataFileError(f"transactions.json has a problem: {error}") from error
        user = User(self._user_name)
        user.add_account(account)
        self._user, self._account = user, account
        self._categories = self._file_manager.load_categories()
        self._budgets = self._file_manager.load_budgets()

    def save_data(self) -> None:
        """Write everything back to the JSON files."""
        self._file_manager.save_transactions(self._account.transactions)
        self._file_manager.save_categories(self._categories)
        self._file_manager.save_budgets(self._budgets)

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------
    def _find_category(self, name: str) -> Category:
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Category is required")
        wanted = name.strip().lower()
        for category in self._categories:
            if category.name.lower() == wanted:
                return category
        raise ValidationError(f"Category {name!r} does not exist")

    def _check_category(self, label: str, name: str) -> str:
        """Category must exist and suit the type. Returns the stored spelling of the name."""
        category = self._find_category(name)
        if category.kind not in (label.lower(), "both"):
            raise ValidationError(f"Category {category.name!r} is for {category.kind} only")
        return category.name

    def _next_transaction_id(self) -> int:
        ids = [tx.id for tx in self._account.transactions]
        return max(ids, default=0) + 1

    # ------------------------------------------------------------------
    # transactions: create, read, update, delete
    # ------------------------------------------------------------------
    def get_transactions(self) -> list[Transaction]:
        return self._account.transactions

    def add_transaction(self, tx_or_type: Transaction | str, amount: float | None = None,
                        date: str | None = None, category: str | None = None,
                        note: str = "", extra: str = "") -> Transaction:
        """Add a transaction.

        Two ways to call it:
          add_transaction("expense", 50, "2026-10-04", "Food", "Lunch", "card")   # from the GUI form
          add_transaction(Expense(...))                                         # a ready-made object
        `extra` is the income source or the expense payment method.
        """
        if isinstance(tx_or_type, Transaction):
            tx = tx_or_type
            tx.category = self._check_category(tx.label(), tx.category)
        else:
            kind = str(tx_or_type).strip().lower()
            if kind not in ("income", "expense"):
                raise ValidationError("Type must be Income or Expense")
            if amount is None or date is None:
                raise ValidationError("Amount and date are required")
            name = self._check_category(kind, category if category is not None else "")
            new_id = self._next_transaction_id()
            if kind == "income":
                tx = Income(new_id, amount, date, name, note, extra)
            else:
                tx = Expense(new_id, amount, date, name, note, extra or "cash")
        self._account.add_transaction(tx)
        self.save_data()
        return tx

    def update_transaction(self, tx_id: int, updated_data: dict[str, Any] | None = None,
                           **fields: Any) -> Transaction:
        """Change fields of a transaction. All-or-nothing: if one value is invalid, nothing changes."""
        changes: dict[str, Any] = dict(updated_data or {})
        changes.update(fields)
        tx = self._account.find_by_id(tx_id)            # NotFoundError if missing
        for key in changes:
            if key not in EDITABLE_FIELDS or not hasattr(tx, key):
                raise ValidationError(f"Field {key!r} cannot be changed on an {tx.label()}")
        old_values = {key: getattr(tx, key) for key in changes}
        try:
            for key, value in changes.items():
                if key == "category":
                    value = self._check_category(tx.label(), value)
                setattr(tx, key, value)                  # goes through the validating setters
        except FinanceError:
            for key, value in old_values.items():        # undo anything already changed
                setattr(tx, key, value)
            raise
        self.save_data()
        return tx

    def delete_transaction(self, tx_id: int) -> None:
        self._account.remove_transaction(tx_id)          # NotFoundError if missing
        self.save_data()

    # ------------------------------------------------------------------
    # search and filter
    # ------------------------------------------------------------------
    def search(self, text: str) -> list[Transaction]:
        """Transactions whose note or category contains the text (not case sensitive)."""
        needle = text.strip().lower()
        return [tx for tx in self._account.transactions
                if needle in tx.note.lower() or needle in tx.category.lower()]

    def filter(self, category: str | None = None, tx_type: str | None = None,
               date_from: str | None = None, date_to: str | None = None) -> list[Transaction]:
        """Keep only transactions matching every criterion that is not None."""
        result = self._account.transactions
        if category is not None:
            result = [tx for tx in result if tx.category.lower() == category.lower()]
        if tx_type is not None:
            result = [tx for tx in result if tx.label().lower() == tx_type.lower()]
        if date_from is not None:
            result = [tx for tx in result if tx.date >= date_from]
        if date_to is not None:
            result = [tx for tx in result if tx.date <= date_to]
        return result

    # ------------------------------------------------------------------
    # categories
    # ------------------------------------------------------------------
    def get_categories(self) -> list[Category]:
        return list(self._categories)

    def add_category(self, name: str, kind: str = "both") -> Category:
        new_id = max((c.id for c in self._categories), default=0) + 1
        category = Category(new_id, name, kind)         # validates name and kind
        if any(c.name.lower() == category.name.lower() for c in self._categories):
            raise ValidationError(f"Category {category.name!r} already exists")
        self._categories.append(category)
        self.save_data()
        return category

    def delete_category(self, name: str) -> None:
        category = self._find_category(name)
        in_transactions = any(tx.category == category.name for tx in self._account.transactions)
        in_budgets = any(b.category == category.name for b in self._budgets)
        if in_transactions or in_budgets:
            raise ValidationError(f"Category {category.name!r} is in use and cannot be deleted")
        self._categories.remove(category)
        self.save_data()

    # ------------------------------------------------------------------
    # budgets
    # ------------------------------------------------------------------
    def get_budgets(self) -> list[Budget]:
        return list(self._budgets)

    def add_budget(self, category: str, limit: float, month: str) -> Budget:
        name = self._check_category("expense", category)
        budget = Budget(name, limit, month)             # validates limit >= 0 and month format
        if any(b.category == name and b.month == month for b in self._budgets):
            raise BudgetError(f"A budget for {name!r} in {month} already exists")
        self._budgets.append(budget)
        self.save_data()
        return budget

    def delete_budget(self, category: str, month: str) -> None:
        for budget in self._budgets:
            if budget.category.lower() == category.lower() and budget.month == month:
                self._budgets.remove(budget)
                self.save_data()
                return
        raise NotFoundError(f"No budget for {category!r} in {month}")

    # ------------------------------------------------------------------
    # summaries (always calculated from the data, never typed in)
    # ------------------------------------------------------------------
    def monthly_summary(self, year: int, month: int) -> dict[str, float]:
        if not 1 <= month <= 12:
            raise ValidationError("Month must be between 1 and 12")
        prefix = f"{year:04d}-{month:02d}"
        income = sum(tx.amount for tx in self._account.transactions
                     if isinstance(tx, Income) and tx.date.startswith(prefix))
        expenses = sum(tx.amount for tx in self._account.transactions
                       if isinstance(tx, Expense) and tx.date.startswith(prefix))
        return {"total_income": round(income, 2), "total_expenses": round(expenses, 2),
                "net": round(income - expenses, 2)}

    def budget_status(self, month: str) -> list[dict[str, Any]]:
        transactions = self._account.transactions
        return [
            {"category": b.category, "limit": b.limit, "spent": b.spent(transactions),
             "remaining": b.remaining(transactions), "exceeded": b.is_exceeded(transactions)}
            for b in self._budgets if b.month == month
        ]

    def dashboard_data(self) -> dict[str, Any]:
        today = dt.date.today()
        month_key = today.strftime("%Y-%m")
        summary = self.monthly_summary(today.year, today.month)
        transactions = self._account.transactions
        total_income = sum(tx.amount for tx in transactions if isinstance(tx, Income))
        total_expenses = sum(tx.amount for tx in transactions if isinstance(tx, Expense))
        spending: dict[str, float] = {}
        for tx in transactions:
            if isinstance(tx, Expense):
                spending[tx.category] = spending.get(tx.category, 0.0) + tx.amount
        top = max(spending, key=lambda name: spending[name]) if spending else None
        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "balance": self._account.balance(),
            "month": month_key,
            "month_income": summary["total_income"],
            "month_expenses": summary["total_expenses"],
            "month_net": summary["net"],
            "budgets_exceeded": sum(1 for s in self.budget_status(month_key) if s["exceeded"]),
            "top_spending_category": top,
            "transaction_count": len(transactions),
        }
