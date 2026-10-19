# Test document: Personal Finance Management System

## 1. Purpose and scope

This document lists the test scenarios for the system, what each one checks, and the result of the latest run. The tests cover the three code layers (models, file handling, service/business rules) and the Tkinter interface.

## 2. How to run

From the project root:

```bash
python Test/test_models.py
python Test/test_file_manager.py
python Test/test_services.py
```

Every test uses a temporary folder, so the real files in `data/` are never touched.

## 3. Test environment

| Item | Value |
|---|---|
| Python | 3.12.3 (project also written for 3.13) |
| OS | Ubuntu Linux (headless, virtual display for the GUI check) |
| Libraries | standard library, `matplotlib` 3.10 and `tkinter` for the GUI |

## 4. Summary

| Suite | File | Tests | Passed | Failed |
|---|---|---|---|---|
| Models | `Test/test_models.py` | 14 | 14 | 0 |
| File handling | `Test/test_file_manager.py` | 7 | 7 | 0 |
| Service / business rules | `Test/test_services.py` | 13 | 13 | 0 |
| **Total automated** | | **34** | **34** | **0** |
| GUI scenarios (section 8) | driven through the real window | 21 | 21 | 0 |

## 5. Service-layer scenarios (`test_services.py`)

| ID | Type | Scenario | Input | Expected result | Result |
|---|---|---|---|---|---|
| 01 | Success | Add income updates the balance | Income 5000, Salary, 2026-10-01 | Transaction gets ID 1, balance is 5000 | PASS |
| 02 | Success | Data survives a restart | Add an expense, then create a new manager on the same folder | The expense (120.50) is loaded back | PASS |
| 03 | Success | Update then delete | Change amount 50 to 75, then delete | New amount is saved; list is empty after delete | PASS |
| 04 | Invalid input | Text amount | Amount `"abc"` | `ValidationError`, nothing is stored | PASS |
| 05 | Invalid input | Impossible date | Date `2026-13-45` | `ValidationError`, nothing is stored | PASS |
| 06 | Invalid input | Missing or unknown category | `""`, `"   "`, `"NoSuchCategory"` | `ValidationError` for each | PASS |
| 07 | Business rule | Amount must be positive | Amount `0` and `-5` | `ValidationError` for each | PASS |
| 08 | Business rule | Budget cannot be negative | Limit `-100` | `ValidationError`, no budget stored | PASS |
| 09 | Edge case | Empty data | New manager with no transactions | Summary is all zeros, no top category, no crash | PASS |
| 10 | Edge case | Corrupt data file | `transactions.json` overwritten with invalid JSON | `DataFileError` whose message says "corrupted" | PASS |
| 11 | Extra | Search and filter | Three transactions in two months | Search "grocer" gives 1; type filter gives 2; date range gives 2; category filter (any case) gives 1 | PASS |
| 12 | Extra | Budget overspending | Budget 200 for Food, expense 250 | spent 250, remaining -50, exceeded; a second budget for the same category and month raises `BudgetError` | PASS |
| 13 | Extra | Category in use, failed update, missing ID | Delete "Food" while used; update with a bad date; delete ID 999 | Delete refused; amount stays 40 (rolled back); `NotFoundError` | PASS |

## 6. Model scenarios (`test_models.py`)

| ID | Scenario | Input | Expected result | Result |
|---|---|---|---|---|
| M01 | Income and expense signs | Income 8000, Expense 320.5 | `signed_amount()` is +8000 and -320.5; labels are "Income" and "Expense" | PASS |
| M02 | Bad amounts rejected | -5, 0, `"abc"`, `None`, NaN, infinity | `ValidationError` for each | PASS |
| M03 | Bad dates rejected | `2026-13-40`, `2026-1-5`, `04/10/2026`, empty, text | `ValidationError` for each | PASS |
| M04 | Empty category and bad ID | Category `""`, `"   "`, `None`; ID 0, -1, `"1"`, 1.5 | `ValidationError` for each | PASS |
| M05 | Abstract parent | `Transaction(...)` directly | `TypeError` (cannot instantiate an abstract class) | PASS |
| M06 | Setters validate; ID read-only | Set amount 12.345, then -1; assign `id` | Amount rounded to 2 places; -1 rejected and the value is unchanged; `id` cannot be assigned | PASS |
| M07 | Dictionary round trip | `to_dict()` then `from_dict()` for Income and Expense | Same class and same data come back | PASS |
| M08 | Bad records | Unknown type, missing amount, negative amount | `ValidationError` for each | PASS |
| M09 | Account balance | Opening 100, income 8000, expense 320.5 | Balance 7779.5 | PASS |
| M10 | Account rules | Add same ID twice; find/remove ID 99; modify the returned list | `ValidationError`; `NotFoundError`; the account is unchanged (list is a copy) | PASS |
| M11 | Account and user names | Empty names, text opening balance, duplicate account, unknown account | `ValidationError` / `NotFoundError` as appropriate | PASS |
| M12 | Budget spending | Mixed months, categories and an income | Only expenses of the same category and month are counted; exceeded only when spent is above the limit (equal is OK) | PASS |
| M13 | Budget validation | Limit -1 or text; empty category; bad months; limit 0 | `ValidationError` for the bad ones; limit 0 is accepted | PASS |
| M14 | Category validation | ID 0, empty name, unknown kind; missing field; no kind given | `ValidationError`; kind defaults to "both" | PASS |

## 7. File-handling scenarios (`test_file_manager.py`)

| ID | Scenario | Input | Expected result | Result |
|---|---|---|---|---|
| F01 | First run | Folder that does not exist yet | Folder and `categories.json` are created with the six default categories; transactions and budgets are empty | PASS |
| F02 | Transactions round trip | Save one Income and one Expense, load again | Same data and the right classes | PASS |
| F03 | Budgets round trip | Save and load one budget | Same data | PASS |
| F04 | Corrupt JSON | Invalid text in `transactions.json` | `DataFileError` ("corrupted") | PASS |
| F05 | Wrong JSON shape | A JSON object instead of a list | `DataFileError` | PASS |
| F06 | Invalid records | Negative amount, missing field, negative budget, unknown category kind | `DataFileError` for each | PASS |
| F07 | Safe saving | Save transactions | No leftover `.tmp` file | PASS |

## 8. GUI scenarios

These were run by driving the real Tkinter window (`FinanceApp`) with the real `FinanceManager` on a copy of the sample data. Message boxes and Yes/No prompts were answered by the test script instead of being shown.

| ID | Scenario | Action | Expected result | Result |
|---|---|---|---|---|
| G01 | Start-up | Open the app on the sample data | 5 rows in the table, 6 categories listed; dashboard shows income $8600.00, expenses $1910.50, balance $6689.50 | PASS |
| G02 | Text amount | Save an expense with amount `abc` | Error box "Amount must be a number"; table unchanged | PASS |
| G03 | Bad date | Save with date `2026-13-45` | Error box about the date; table unchanged | PASS |
| G04 | No category | Save with no category selected | Error box "Category is required" | PASS |
| G05 | Wrong category kind | Save an Income in the expense-only category Food | Error box "Category 'Food' is for expense only" | PASS |
| G06 | Valid transaction | Save an expense of 45.50 in Food | "Transaction saved" message; table shows 6 rows | PASS |
| G07 | Budget, category, filter, delete | Set Food budget 30; add category Gym; filter Expense + search "lunch"; delete a row | Budget row shows EXCEEDED; 7 categories; 1 filtered row; table back to 5 rows after delete | PASS |
| G08 | Replace a budget | Set Food budget 500 while 30 exists; answer Yes to the prompt | Only one Food budget remains, limit 500, status OK | PASS |
| G09 | Decline the replace | Same, but answer No | Nothing changes (limit stays 30) | PASS |
| G10 | Replace with an invalid value | Set Food budget `-5` while 30 exists | Error box; the old budget (30) is still there | PASS |
| G11 | Delete budget, nothing selected | Press Delete Selected Budget | Error box "Select a budget row first." | PASS |
| G12 | Delete a budget | Select the Food row, press Delete; answer No, then Yes | No keeps the budget; Yes removes it from the table and the data | PASS |
| G13 | Edit, nothing selected | Press Edit Selected with no row selected | Error box "Select a row first." | PASS |
| G14 | Start an edit | Select transaction 3, press Edit Selected | Form is filled with its values; title "Edit Transaction 3"; button reads "Update Transaction"; type buttons are disabled; Cancel Edit is visible | PASS |
| G15 | Invalid edit | Change amount to `abc`; then amount 400 with date `2026-13-45` | Error box each time; still in edit mode; the stored amount stays 320.50 (nothing half-changed) | PASS |
| G16 | Valid edit | Amount 400, note "Big shop", press Update | "Transaction updated" message; table shows 400.00; form returns to "add" mode | PASS |
| G17 | Cancel an edit | Start editing transaction 2, press Cancel Edit | Form is cleared and back in "add" mode; data unchanged | PASS |
| G18 | Edit to a wrong-kind category | Edit an expense and choose the income-only category Salary | Error box; category unchanged | PASS |
| G19 | Delete the row being edited | Start editing transaction 5, press Delete Selected | Row is deleted and the form leaves edit mode | PASS |
| G20 | Saved to disk | Reload the data folder with a new manager | The edited amount (400) is there | PASS |
| G21 | No fake mode | Inspect the module; run `python main.py` | No `StandaloneManager` or dummy classes exist; the program starts normally | PASS |

## 9. Defects found during testing

| # | Where | Problem | Status |
|---|---|---|---|
| 1 | `GUI/app.py` | The file still contained four unresolved Git merge conflicts (`<<<<<<< HEAD` ... `>>>>>>>`), so Python stopped with a `SyntaxError` and the app could not start | Fixed: the `HEAD` side was kept in each conflict (it matches the current `FinanceManager`); the other side called methods that do not exist (`get_summary`, `DummyFileManager`) |
| 2 | `GUI/app.py` | Leftover debug code: `print("Hi")`, a `#Hi` comment, and a duplicated block of `matplotlib` imports | Fixed |
| 3 | `GUI/test.py` | Placeholder file containing only `print("Hello")` | Delete from the repo |
| 4 | GUI budgets tab | A budget could not be changed or deleted once set (duplicate check refused a second budget and there was no delete button) | Fixed: setting a budget again replaces it after a confirmation (the old one is restored if the new value is invalid), and a Delete Selected Budget button was added (G08 to G12) |
| 5 | `GUI/app.py` | If the backend failed to load, the app silently switched to a fake in-memory manager with dummy data, which hid real problems | Fixed: the fake manager and dummy classes were removed; `main.py` shows the real error (G21) |
| 6 | GUI transactions tab | The service layer could update a transaction but the GUI had no way to do it | Fixed: Edit Selected and Cancel Edit buttons were added (G13 to G19) |
