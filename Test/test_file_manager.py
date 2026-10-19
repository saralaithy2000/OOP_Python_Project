"""Unit tests for FileManager (JSON saving and loading).

Run from the project root:   python Test/test_file_manager.py
(also works with pytest if you have it installed)
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exceptions import DataFileError
from file_manager.file_manager import FileManager
from models.budget import Budget
from models.expense import Expense
from models.income import Income


def write(folder, filename, text):
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as file:
        file.write(text)


def raises_data_error(function):
    try:
        function()
    except DataFileError as error:
        return str(error)
    return None


def test_f01_first_run_creates_default_files():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(os.path.join(folder, "new_data"))     # folder does not exist yet
        assert manager.load_transactions() == []
        assert [c.name for c in manager.load_categories()][:3] == ["Salary", "Freelance", "Food"]
        assert manager.load_budgets() == []
        assert os.path.exists(os.path.join(folder, "new_data", "categories.json"))


def test_f02_transactions_round_trip():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(folder)
        original = [Income(1, 8000, "2026-10-01", "Salary", "Pay", "WE"),
                    Expense(2, 320.5, "2026-10-04", "Food", "Groceries", "card")]
        manager.save_transactions(original)
        loaded = manager.load_transactions()
        assert [t.to_dict() for t in loaded] == [t.to_dict() for t in original]
        assert [type(t).__name__ for t in loaded] == ["Income", "Expense"]


def test_f03_budgets_round_trip():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(folder)
        manager.save_budgets([Budget("Food", 300, "2026-10")])
        assert [b.to_dict() for b in manager.load_budgets()] == [
            {"category": "Food", "limit": 300.0, "month": "2026-10"}]


def test_f04_corrupt_json_gives_data_file_error():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(folder)
        write(folder, "transactions.json", "[ this is not valid json")
        message = raises_data_error(manager.load_transactions)
        assert message is not None and "corrupted" in message


def test_f05_wrong_json_shape_gives_data_file_error():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(folder)
        write(folder, "transactions.json", '{"not": "a list"}')
        assert raises_data_error(manager.load_transactions) is not None


def test_f06_invalid_records_give_data_file_error():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(folder)
        bad_amount = [{"id": 1, "type": "expense", "amount": -5, "date": "2026-10-01", "category": "Food"}]
        missing_field = [{"id": 1, "type": "expense", "date": "2026-10-01", "category": "Food"}]
        for records in (bad_amount, missing_field):
            write(folder, "transactions.json", json.dumps(records))
            assert raises_data_error(manager.load_transactions) is not None
        write(folder, "budgets.json", json.dumps([{"category": "Food", "limit": -1, "month": "2026-10"}]))
        assert raises_data_error(manager.load_budgets) is not None
        write(folder, "categories.json", json.dumps([{"id": 1, "name": "Food", "kind": "weird"}]))
        assert raises_data_error(manager.load_categories) is not None


def test_f07_save_leaves_no_temporary_file():
    with tempfile.TemporaryDirectory() as folder:
        manager = FileManager(folder)
        manager.save_transactions([Expense(1, 5, "2026-10-01", "Food")])
        assert not [name for name in os.listdir(folder) if name.endswith(".tmp")]


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
