# Personal Finance Management System

A desktop application for tracking income, expenses and monthly budgets. It is written in Python with `tkinter` for the interface and JSON files for storage, and it is built around object-oriented design: abstraction, inheritance, polymorphism, encapsulation and composition.

## Features

- **Dashboard**: total income, total expenses and net balance, plus two charts (expenses by category, income vs expenses).
- **Transactions**: add income and expenses, edit a transaction (select a row and press *Edit Selected*), search by note or category, filter by type and category, delete a transaction.
- **Budgets**: set a monthly limit for an expense category (setting it again replaces the old limit after a confirmation), delete a budget, and see spent, remaining and an `EXCEEDED` flag for the current month.
- **Categories**: view and add categories.
- **Automatic saving**: every change is written to the JSON files, and the data is saved again when the window closes.
- **Friendly errors**: invalid input (text amount, impossible date, unknown category, negative budget...) shows a message box instead of crashing. A damaged data file stops the app with a clear message.

## Requirements

- Python 3.10 or newer (`tkinter` is included with the standard Windows and macOS installers)
- `matplotlib` for the dashboard charts

```bash
pip install matplotlib
```

## How to run

Run everything from the project root (the folder that contains `main.py`):

```bash
python main.py
```

On the first run the app creates `categories.json` and `budgets.json` in `data/`. Sample transactions are already in `data/transactions.json`.

## Project structure

```text
OOP_Python_Project/
├── main.py                     # entry point: loads the data, opens the window, saves on close
├── exceptions.py               # FinanceError and its subclasses
├── models/                     # the domain classes
│   ├── transaction.py          #   abstract parent of Income and Expense
│   ├── income.py
│   ├── expense.py
│   ├── category.py
│   ├── budget.py
│   ├── account.py              #   owns a list of transactions
│   └── user.py                 #   owns accounts
├── file_manager/
│   └── file_manager.py         # the only class that reads and writes JSON
├── services/
│   └── finance_manager.py      # business rules; the only class the GUI talks to
├── GUI/
│   └── app.py                  # tkinter interface (FinanceApp)
├── Test/
│   ├── test_models.py
│   ├── test_file_manager.py
│   └── test_services.py
├── data/
│   └── transactions.json       # sample data
└── docs/
    ├── UML_class_diagram.md
    └── TEST_DOCUMENT.md
```

## Architecture

The program is split into layers, and each layer only talks to the one below it:

```text
GUI (FinanceApp)  ->  FinanceManager  ->  models (Account, Budget, ...)  and  FileManager
```

- The **GUI** only displays data and catches `FinanceError`.
- **FinanceManager** holds every business rule, so the rules live in one place.
- **FileManager** is the only class that touches the disk, so the storage format can change without touching anything else.

The full class diagram is in [`docs/UML_class_diagram.md`](docs/UML_class_diagram.md).

## OOP concepts used

| Concept | Where |
|---|---|
| Abstraction | `Transaction` is an abstract class (`ABC`); it cannot be created directly and declares the abstract methods `signed_amount()` and `label()` |
| Inheritance | `Income` and `Expense` extend `Transaction` and add `source` / `payment_method` |
| Polymorphism | `Account.balance()` sums `tx.signed_amount()` without checking the type; each class returns its own sign |
| Encapsulation | Private fields (`_amount`, `_date`...) behind validated properties; `Account.transactions` returns a copy so outside code cannot bypass the checks |
| Composition | `User` has `Account`s; `Account` has `Transaction`s; `FinanceManager` has a `User`, categories and budgets |
| Factory method | `Transaction.from_dict()` builds an `Income` or an `Expense` from a JSON record |
| Custom exceptions | `ValidationError`, `NotFoundError`, `BudgetError` and `DataFileError` all extend `FinanceError` |

## Business rules

1. A transaction amount must be a number greater than zero.
2. Dates must be real dates in the format `YYYY-MM-DD`.
3. Every transaction needs a category that exists, and its kind must suit the type (an expense cannot use an income-only category).
4. A budget limit cannot be negative, its month must be `YYYY-MM`, and there is at most one budget per category per month.
5. Transaction IDs are unique.
6. A category that is used by a transaction or a budget cannot be deleted.
7. Updating a transaction is all-or-nothing: if one value is invalid, nothing changes.

## Data files

All files are lists of records in the `data/` folder.

```json
// transactions.json
{"id": 3, "type": "expense", "amount": 320.5, "date": "2026-10-04", "category": "Food", "note": "Groceries", "payment_method": "card"}
{"id": 1, "type": "income",  "amount": 8000.0, "date": "2026-10-01", "category": "Salary", "note": "October salary", "source": "WE"}

// categories.json
{"id": 1, "name": "Food", "kind": "expense"}        // kind: "income", "expense" or "both"

// budgets.json
{"category": "Food", "limit": 2000, "month": "2026-10"}
```

## Running the tests

```bash
python Test/test_models.py
python Test/test_file_manager.py
python Test/test_services.py
```

Each file prints `PASS` / `FAIL` per test and a summary. `pytest` also works if it is installed. See [`docs/TEST_DOCUMENT.md`](docs/TEST_DOCUMENT.md) for the scenarios and results.

## Known limitations

- Budgets always apply to the current month.
- The GUI supports one user and one account, and shows amounts in `$`.
- When editing a transaction, its type (income or expense) cannot be changed, and the income source / payment method are not shown in the GUI (they keep their stored values).

## Team

| Student | Part |
|---|---|
| Student A (Aya) | `exceptions.py`, `models/`, `file_manager/`, `data/`, model and file tests |
| Student B (Sara Laithy) | `GUI/app.py`, `services/finance_manager.py`, service tests |
