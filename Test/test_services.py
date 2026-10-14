"""Test scenarios for the Personal Finance system.

Run from the project root:   python Test/test_services.py
(also works with pytest if you have it installed)

Scenarios 1-3 success, 4-6 invalid input, 7-8 business-rule violations, 9-10 edge cases,
11-13 extra checks.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import BudgetError, DataFileError, NotFoundError, ValidationError
from file_manager.file_manager import FileManager
from services.finance_manager import FinanceManager


def new_manager(folder: str) -> FinanceManager:
    return FinanceManager(FileManager(folder))


# ---------- 3 success scenarios ----------
def test_01_add_income_updates_balance():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        tx = manager.add_transaction("income", 5000, "2026-10-01", "Salary", "October", "WE")
        assert tx.id == 1 and tx.signed_amount() == 5000
        assert manager.dashboard_data()["balance"] == 5000


def test_02_data_survives_restart():
    with tempfile.TemporaryDirectory() as folder:
        new_manager(folder).add_transaction("expense", 120.5, "2026-10-02", "Food", "Groceries", "card")
        reloaded = new_manager(folder)                  # a brand new manager reads the files
        transactions = reloaded.get_transactions()
        assert len(transactions) == 1 and transactions[0].amount == 120.5


def test_03_update_then_delete():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        tx = manager.add_transaction("expense", 50, "2026-10-03", "Transport", "Taxi")
        manager.update_transaction(tx.id, amount=75, note="Taxi to work")
        assert new_manager(folder).get_transactions()[0].amount == 75
        manager.delete_transaction(tx.id)
        assert new_manager(folder).get_transactions() == []


# ---------- 3 invalid input scenarios ----------
def test_04_text_amount_rejected():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        try:
            manager.add_transaction("expense", "abc", "2026-10-03", "Food")
            assert False, "should have been rejected"
        except ValidationError:
            assert manager.get_transactions() == []


def test_05_invalid_date_rejected():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        try:
            manager.add_transaction("expense", 10, "2026-13-45", "Food")
            assert False, "should have been rejected"
        except ValidationError:
            assert manager.get_transactions() == []


def test_06_missing_category_rejected():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        for bad in ("", "   ", "NoSuchCategory"):
            try:
                manager.add_transaction("expense", 10, "2026-10-03", bad)
                assert False, f"category {bad!r} should have been rejected"
            except ValidationError:
                pass


# ---------- 2 business-rule violations ----------
def test_07_amount_must_be_positive():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        for bad in (0, -5):
            try:
                manager.add_transaction("income", bad, "2026-10-03", "Salary")
                assert False, f"amount {bad} should have been rejected"
            except ValidationError:
                pass


def test_08_budget_cannot_be_negative():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        try:
            manager.add_budget("Food", -100, "2026-10")
            assert False, "should have been rejected"
        except ValidationError:
            assert manager.get_budgets() == []


# ---------- 2 edge cases ----------
def test_09_empty_data_gives_zeros_not_a_crash():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        summary = manager.monthly_summary(2026, 10)
        assert summary == {"total_income": 0.0, "total_expenses": 0.0, "net": 0.0}
        data = manager.dashboard_data()
        assert data["balance"] == 0 and data["top_spending_category"] is None


def test_10_corrupt_file_gives_clear_error():
    with tempfile.TemporaryDirectory() as folder:
        new_manager(folder).add_transaction("income", 10, "2026-10-01", "Salary")
        with open(os.path.join(folder, "transactions.json"), "w", encoding="utf-8") as file:
            file.write("[ not valid json")
        try:
            new_manager(folder)
            assert False, "should have raised DataFileError"
        except DataFileError as error:
            assert "corrupted" in str(error)


# ---------- extra checks ----------
def test_11_search_and_filter():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        manager.add_transaction("income", 8000, "2026-10-01", "Salary", "October salary")
        manager.add_transaction("expense", 300, "2026-10-04", "Food", "Groceries")
        manager.add_transaction("expense", 90, "2026-11-02", "Transport", "Fuel")
        assert len(manager.search("grocer")) == 1
        assert len(manager.filter(tx_type="expense")) == 2
        assert len(manager.filter(date_from="2026-10-01", date_to="2026-10-31")) == 2
        assert len(manager.filter(category="food")) == 1


def test_12_budget_status_flags_overspending():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        manager.add_budget("Food", 200, "2026-10")
        manager.add_transaction("expense", 250, "2026-10-04", "Food", "Party")
        status = manager.budget_status("2026-10")[0]
        assert status["spent"] == 250 and status["remaining"] == -50 and status["exceeded"] is True
        try:
            manager.add_budget("Food", 300, "2026-10")
            assert False, "duplicate budget should be rejected"
        except BudgetError:
            pass


def test_13_category_in_use_and_failed_update_rolls_back():
    with tempfile.TemporaryDirectory() as folder:
        manager = new_manager(folder)
        tx = manager.add_transaction("expense", 40, "2026-10-04", "Food", "Lunch")
        try:
            manager.delete_category("Food")
            assert False, "category in use must not be deleted"
        except ValidationError:
            pass
        try:
            manager.update_transaction(tx.id, amount=99, date="not-a-date")
            assert False, "bad date must be rejected"
        except ValidationError:
            assert manager.get_transactions()[0].amount == 40   # amount was NOT changed
        try:
            manager.delete_transaction(999)
            assert False
        except NotFoundError:
            pass


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items()) if name.startswith("test_")]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS", name)
        except Exception as error:  # noqa: BLE001 - we want to report any failure
            failed += 1
            print("FAIL", name, "->", repr(error))
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
