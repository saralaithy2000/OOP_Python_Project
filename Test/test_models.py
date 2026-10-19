"""Unit tests for the model classes (Student A part).

Run from the project root:   python Test/test_models.py
(also works with pytest if you have it installed)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import NotFoundError, ValidationError
from models.account import Account
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from models.income import Income
from models.transaction import Transaction
from models.user import User


def rejects(error_type, function):
    """True if calling function() raises error_type."""
    try:
        function()
    except error_type:
        return True
    return False


# ---------- Transaction, Income, Expense ----------
def test_m01_income_and_expense_have_opposite_signs():
    assert Income(1, 8000, "2026-10-01", "Salary").signed_amount() == 8000
    assert Expense(2, 320.5, "2026-10-04", "Food").signed_amount() == -320.5
    assert Income(1, 1, "2026-10-01", "Salary").label() == "Income"
    assert Expense(2, 1, "2026-10-01", "Food").label() == "Expense"


def test_m02_bad_amounts_rejected():
    for bad in (-5, 0, "abc", None, float("nan"), float("inf")):
        assert rejects(ValidationError, lambda: Expense(3, bad, "2026-10-04", "Food")), bad


def test_m03_bad_dates_rejected():
    for bad in ("2026-13-40", "2026-1-5", "04/10/2026", "", "not a date"):
        assert rejects(ValidationError, lambda: Expense(3, 5, bad, "Food")), bad


def test_m04_empty_category_and_bad_id_rejected():
    for bad in ("", "   ", None):
        assert rejects(ValidationError, lambda: Expense(3, 5, "2026-10-04", bad)), bad
    for bad in (0, -1, "1", 1.5):
        assert rejects(ValidationError, lambda: Expense(bad, 5, "2026-10-04", "Food")), bad


def test_m05_transaction_is_abstract():
    assert rejects(TypeError, lambda: Transaction(1, 5, "2026-10-04", "Food"))


def test_m06_setters_validate_and_id_is_read_only():
    tx = Expense(1, 10, "2026-10-04", "Food")
    tx.amount = 12.345
    assert tx.amount == 12.35 or tx.amount == 12.34          # rounded to 2 places
    assert rejects(ValidationError, lambda: setattr(tx, "amount", -1))
    assert tx.amount in (12.34, 12.35)                        # failed set changed nothing
    assert rejects(AttributeError, lambda: setattr(tx, "id", 99))


def test_m07_dict_round_trip_keeps_the_right_class():
    income = Income(1, 600, "2026-10-08", "Freelance", "Side project", "Client")
    expense = Expense(2, 90, "2026-10-06", "Transport", "Fuel", "cash")
    for original in (income, expense):
        copy = Transaction.from_dict(original.to_dict())
        assert type(copy) is type(original) and copy.to_dict() == original.to_dict()


def test_m08_from_dict_rejects_bad_records():
    good = {"id": 1, "type": "income", "amount": 5, "date": "2026-10-01", "category": "Salary"}
    assert rejects(ValidationError, lambda: Transaction.from_dict({**good, "type": "gift"}))
    assert rejects(ValidationError, lambda: Transaction.from_dict({k: v for k, v in good.items() if k != "amount"}))
    assert rejects(ValidationError, lambda: Transaction.from_dict({**good, "amount": -5}))


# ---------- Account and User ----------
def test_m09_account_balance_uses_opening_balance():
    account = Account("Main", 100)
    account.add_transaction(Income(1, 8000, "2026-10-01", "Salary"))
    account.add_transaction(Expense(2, 320.5, "2026-10-04", "Food"))
    assert account.balance() == 7779.5


def test_m10_account_duplicate_missing_and_copy():
    account = Account("Main")
    tx = Expense(1, 10, "2026-10-04", "Food")
    account.add_transaction(tx)
    assert rejects(ValidationError, lambda: account.add_transaction(tx))     # duplicate ID
    assert rejects(NotFoundError, lambda: account.find_by_id(99))
    assert rejects(NotFoundError, lambda: account.remove_transaction(99))
    account.transactions.clear()                                             # a copy: no effect
    assert len(account.transactions) == 1
    account.remove_transaction(1)
    assert account.transactions == [] and account.balance() == 0


def test_m11_account_and_user_names_validated():
    assert rejects(ValidationError, lambda: Account("  "))
    assert rejects(ValidationError, lambda: Account("Main", "abc"))
    assert rejects(ValidationError, lambda: User(""))
    user = User("Aya")
    user.add_account(Account("Main"))
    assert rejects(ValidationError, lambda: user.add_account(Account("Main")))
    assert rejects(NotFoundError, lambda: user.get_account("Savings"))
    assert user.get_account("Main").name == "Main"


# ---------- Budget and Category ----------
def test_m12_budget_counts_only_matching_expenses():
    transactions = [
        Expense(1, 200, "2026-10-04", "Food"),
        Expense(2, 100, "2026-10-20", "Food"),
        Expense(3, 999, "2026-11-02", "Food"),         # other month
        Expense(4, 50, "2026-10-05", "Transport"),     # other category
        Income(5, 500, "2026-10-06", "Food"),          # income is not spending
    ]
    budget = Budget("Food", 250, "2026-10")
    assert budget.spent(transactions) == 300
    assert budget.remaining(transactions) == -50
    assert budget.is_exceeded(transactions) is True
    assert Budget("Food", 300, "2026-10").is_exceeded(transactions) is False   # exactly the limit is OK


def test_m13_budget_validation():
    assert rejects(ValidationError, lambda: Budget("Food", -1, "2026-10"))
    assert rejects(ValidationError, lambda: Budget("Food", "abc", "2026-10"))
    assert rejects(ValidationError, lambda: Budget("", 100, "2026-10"))
    for bad in ("2026-13", "2026-1", "October", "2026-10-01"):
        assert rejects(ValidationError, lambda: Budget("Food", 100, bad)), bad
    assert Budget("Food", 0, "2026-10").limit == 0                              # zero is allowed


def test_m14_category_validation_and_round_trip():
    assert rejects(ValidationError, lambda: Category(0, "Food"))
    assert rejects(ValidationError, lambda: Category(1, "  "))
    assert rejects(ValidationError, lambda: Category(1, "Food", "weird"))
    category = Category.from_dict({"id": 3, "name": "Food", "kind": "expense"})
    assert category.to_dict() == {"id": 3, "name": "Food", "kind": "expense"}
    assert Category.from_dict({"id": 4, "name": "Misc"}).kind == "both"         # default kind
    assert rejects(ValidationError, lambda: Category.from_dict({"id": 1}))


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS", name)
        except Exception as error:  # noqa: BLE001
            failed += 1
            print("FAIL", name, "->", repr(error))
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
