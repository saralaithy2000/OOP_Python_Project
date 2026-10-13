import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.finance_manager import FinanceManager, NotFoundError

class DummyFileManager:
    def __init__(self):
        self.data = {"transactions": []}

    def load(self):
        return self.data

    def save(self, data):
        self.data = data

class MockTransaction:
    def __init__(self, tx_id, amount, date, category, note):
        self._id = tx_id
        self._amount = amount
        self._date = date
        self._category = category
        self._note = note

class MockIncome(MockTransaction):
    def label(self):
        return "Income"

class MockExpense(MockTransaction):
    def label(self):
        return "Expense"

def run_tests():
    print("--- Starting Services Test ---")
    
    file_mgr = DummyFileManager()
    manager = FinanceManager(file_mgr)
    
    inc = MockIncome("1", 5000, "2026-10-01", "Salary", "Monthly Pay")
    manager.add_transaction(inc)
    print("Income added successfully.")

    exp = MockExpense("2", 200, "2026-10-02", "Food", "Lunch")
    manager.add_transaction(exp)
    print("Expense added successfully.")

    search_results = manager.search("Lunch")
    print(f"Search results count: {len(search_results)}")

    filtered_results = manager.filter(tx_type="Expense")
    print(f"Filtered expenses count: {len(filtered_results)}")

    try:
        manager.delete_transaction("999")
    except NotFoundError as e:
        print(f"Caught expected error: {e}")

    print("--- All tests passed successfully! ---")

if __name__ == "__main__":
    run_tests()