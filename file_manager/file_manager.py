"""FileManager: the ONLY class that reads and writes the JSON files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from exceptions import DataFileError, ValidationError
from models.budget import Budget
from models.category import Category
from models.transaction import Transaction

DEFAULT_CATEGORIES: list[dict[str, Any]] = [
    {"id": 1, "name": "Salary", "kind": "income"},
    {"id": 2, "name": "Freelance", "kind": "income"},
    {"id": 3, "name": "Food", "kind": "expense"},
    {"id": 4, "name": "Transport", "kind": "expense"},
    {"id": 5, "name": "Rent", "kind": "expense"},
    {"id": 6, "name": "Entertainment", "kind": "expense"},
]


class FileManager:
    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir: Path = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)

    # ---------- low-level helpers (private) ----------
    def _read_json(self, filename: str, default: list[dict[str, Any]]) -> list[dict[str, Any]]:
        path = self._data_dir / filename
        if not path.exists():                      # first run: create the file with defaults
            self._write_json(filename, default)
            return list(default)
        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise DataFileError(f"{filename} is corrupted: {error}") from error
        except OSError as error:
            raise DataFileError(f"Cannot read {filename}: {error}") from error
        if not isinstance(data, list):
            raise DataFileError(f"{filename} must contain a list of records")
        return data

    def _write_json(self, filename: str, records: list[dict[str, Any]]) -> None:
        path = self._data_dir / filename
        temp = path.with_suffix(".tmp")
        try:
            with temp.open("w", encoding="utf-8") as file:
                json.dump(records, file, indent=2, ensure_ascii=False)
            temp.replace(path)                     # replace only after a complete write
        except OSError as error:
            raise DataFileError(f"Cannot write {filename}: {error}") from error

    # ---------- public methods ----------
    def load_transactions(self) -> list[Transaction]:
        records = self._read_json("transactions.json", [])
        try:
            return [Transaction.from_dict(record) for record in records]
        except (ValidationError, TypeError, AttributeError) as error:
            raise DataFileError(f"transactions.json contains invalid data: {error}") from error

    def save_transactions(self, transactions: list[Transaction]) -> None:
        self._write_json("transactions.json", [tx.to_dict() for tx in transactions])

    def load_categories(self) -> list[Category]:
        records = self._read_json("categories.json", DEFAULT_CATEGORIES)
        try:
            return [Category.from_dict(record) for record in records]
        except (ValidationError, TypeError, AttributeError) as error:
            raise DataFileError(f"categories.json contains invalid data: {error}") from error

    def save_categories(self, categories: list[Category]) -> None:
        self._write_json("categories.json", [c.to_dict() for c in categories])

    def load_budgets(self) -> list[Budget]:
        records = self._read_json("budgets.json", [])
        try:
            return [Budget.from_dict(record) for record in records]
        except (ValidationError, TypeError, AttributeError) as error:
            raise DataFileError(f"budgets.json contains invalid data: {error}") from error

    def save_budgets(self, budgets: list[Budget]) -> None:
        self._write_json("budgets.json", [b.to_dict() for b in budgets])
