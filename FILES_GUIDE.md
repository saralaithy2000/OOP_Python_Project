# Student A files: what each one is and what to do with it

Copy these into the repo: `exceptions.py`, `models/`, `file_manager/`, `data/transactions.json`.
Do NOT commit: `scratch_a.py` (optional), `data_test/`, any `__pycache__/` folder.

| File | What it does | Why it matters |
|---|---|---|
| exceptions.py | Custom error types: FinanceError (parent), ValidationError, NotFoundError, BudgetError, DataFileError | Every other file raises these. The GUI catches them and shows friendly messages (error handling requirement). |
| models/__init__.py, file_manager/__init__.py | Empty files that mark folders as Python packages | Without them `from models.income import Income` fails. |
| models/transaction.py | Abstract parent of Income and Expense. Private fields, validated properties, to_dict(), from_dict() | Core of your OOP grade: abstraction, encapsulation, properties. Enforces business rule 1 (amount > 0). |
| models/income.py | Income: adds `source`; signed_amount() is +amount | Inheritance and polymorphism. |
| models/expense.py | Expense: adds `payment_method`; signed_amount() is -amount | Inheritance and polymorphism. Expense must have a category (rule 2). |
| models/category.py | Category with validated name and kind | The list of allowed categories, checked by FinanceManager. |
| models/budget.py | Monthly limit per category; spent(), remaining(), is_exceeded() | Budget tracking and rule 3 (limit cannot be negative). |
| models/account.py | Owns a list of transactions; add/find/remove/balance() | Composition. balance() shows polymorphism. |
| models/user.py | Owns accounts; add_account(), get_account() | Composition. |
| file_manager/file_manager.py | The only class that reads and writes JSON files; creates defaults; handles corrupt files | File handling grade. Keeps files separate from business logic. |
| data/transactions.json | Sample data (5 records) | Lets the app and the GUI show real data from the first run. Must stay valid JSON. |
| scratch_a.py | Your personal test script | Proves everything works. Reuse its checks for the Day 6 test scenarios. Run: `python scratch_a.py` from the project root. |

## Rules
- Run Python from the project root (the folder that contains exceptions.py).
- Do not rename methods or change what they take or return without messaging your teammate first.
- Edit only your folders: models/ and file_manager/. Her code lives in gui/, services/, tests/.
- Her sample categories.json and budgets.json must match the format FileManager expects:
  categories: {"id": 1, "name": "Food", "kind": "expense"}   budgets: {"category": "Food", "limit": 2000, "month": "2026-10"}

## Sync to GitHub
1. One time: `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`
2. Accept her collaborator invitation on GitHub (check your email or github.com notifications).
3. `git clone <her-repo-link>` then `cd` into the new folder.
4. Copy the files listed at the top into the cloned folder (merge into existing folders).
5. `git status` to check what will be saved. Only the files above should appear.
6. `git add .` then `git commit -m "Add exceptions, models and FileManager"` then `git push`
7. Open the repo page on github.com and confirm the files are there.
8. Every day after: `git pull` first, then work, then add, commit, push.
