import os
import sys
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from exceptions import FinanceError
    from services.finance_manager import FinanceManager
    from file_manager.file_manager import FileManager
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False
    class FinanceError(Exception):
        pass

class DummyCategory:
    def __init__(self, name):
        self.name = name

class DummyTransaction:
    def __init__(self, id, date, tx_type, category, amount, note):
        self.id = id
        self.date = date
        self.type = tx_type
        self.category = category
        self.amount = float(amount)
        self.note = note
    def label(self):
        return self.type

class StandaloneManager:
    def __init__(self):
        self.transactions = [
            DummyTransaction(1, "2026-10-01", "Income", "Salary", 5000.0, "Monthly Salary"),
            DummyTransaction(2, "2026-10-02", "Expense", "Food", 150.0, "Groceries")
        ]
        self.categories = [DummyCategory("Salary"), DummyCategory("Food"), DummyCategory("Transport"), DummyCategory("Rent"), DummyCategory("Entertainment")]
        self.budgets = {}

    def get_transactions(self):
        return self.transactions

    def get_categories(self):
        return self.categories

    def dashboard_data(self):
        inc = sum(t.amount for t in self.transactions if t.label() == "Income")
        exp = sum(t.amount for t in self.transactions if t.label() == "Expense")
        return {
            "total_income": inc,
            "total_expenses": exp,
            "balance": inc - exp
        }

    def add_transaction(self, tx_type, amount, date, category, note):
        try:
            amt = float(amount)
            if amt <= 0:
                raise FinanceError("Amount must be greater than zero.")
        except ValueError:
            raise FinanceError("Amount must be a valid number.")
        
        new_id = len(self.transactions) + 1
        tx = DummyTransaction(new_id, date, tx_type, category, amt, note)
        self.transactions.append(tx)
        return tx

    def add_category(self, name):
        if not name:
            raise FinanceError("Category name cannot be empty.")
        if any(c.name.lower() == name.lower() for c in self.categories):
            raise FinanceError(f"Category '{name}' already exists.")
        self.categories.append(DummyCategory(name))

    def add_budget(self, category, limit, month):
        try:
            lim = float(limit)
            if lim < 0:
                raise FinanceError("Limit cannot be negative.")
        except ValueError:
            raise FinanceError("Limit must be a valid number.")
        self.budgets[(category, month)] = lim

    def budget_status(self, month):
        statuses = []
        for cat in self.categories:
            lim = self.budgets.get((cat.name, month), 0.0)
            spent = sum(t.amount for t in self.transactions if t.category == cat.name and t.label() == "Expense")
            statuses.append({
                "category": cat.name,
                "limit": lim,
                "spent": spent,
                "remaining": lim - spent,
                "exceeded": spent > lim if lim > 0 else False
            })
        return statuses

    def search(self, text):
        text = text.lower()
        return [t for t in self.transactions if text in t.note.lower() or text in t.category.lower()]

    def filter(self, category=None, tx_type=None):
        res = self.transactions
        if category and category != "All":
            res = [t for t in res if t.category == category]
        if tx_type and tx_type != "All":
            res = [t for t in res if t.label() == tx_type]
        return res

    def delete_transaction(self, tx_id):
        self.transactions = [t for t in self.transactions if t.id != tx_id]


class FinanceApp:
    def __init__(self, root: tk.Tk, manager=None) -> None:
        self.root = root
        if manager is not None:
            self.manager = manager
        else:
            if HAS_BACKEND:
                try:
                    self.manager = FinanceManager(FileManager())
                except Exception:
                    self.manager = StandaloneManager()
            else:
                self.manager = StandaloneManager()

        self.root.title("Personal Finance Management System")
        self.root.geometry("950x750")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_transactions = ttk.Frame(self.notebook)
        self.tab_budgets = ttk.Frame(self.notebook)
        self.tab_categories = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_transactions, text="Transactions")
        self.notebook.add(self.tab_budgets, text="Budgets")
        self.notebook.add(self.tab_categories, text="Categories")

        self.setup_dashboard_tab()
        self.setup_transactions_tab()
        self.setup_budgets_tab()
        self.setup_categories_tab()

        self.refresh_all_data()

    def setup_dashboard_tab(self) -> None:
        summary_frame = ttk.LabelFrame(self.tab_dashboard, text="Financial Summary")
        summary_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_income = ttk.Label(summary_frame, text="Total Income: $0.00", font=("Arial", 11, "bold"), foreground="green")
        self.lbl_income.grid(row=0, column=0, padx=20, pady=10)

        self.lbl_expense = ttk.Label(summary_frame, text="Total Expenses: $0.00", font=("Arial", 11, "bold"), foreground="red")
        self.lbl_expense.grid(row=0, column=1, padx=20, pady=10)

        self.lbl_balance = ttk.Label(summary_frame, text="Net Balance: $0.00", font=("Arial", 11, "bold"), foreground="blue")
        self.lbl_balance.grid(row=0, column=2, padx=20, pady=10)

        chart_frame = ttk.LabelFrame(self.tab_dashboard, text="Visual Analytics")
        chart_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.figure = Figure(figsize=(8, 4.5), dpi=100)
        self.ax1 = self.figure.add_subplot(121)
        self.ax2 = self.figure.add_subplot(122)

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        btn_refresh = ttk.Button(self.tab_dashboard, text="Refresh Dashboard", command=self.refresh_all_data)
        btn_refresh.pack(pady=5)

    def setup_transactions_tab(self) -> None:
        form_frame = ttk.LabelFrame(self.tab_transactions, text="Add New Transaction")
        form_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(form_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar(value="Expense")
        ttk.Radiobutton(form_frame, text="Income", value="Income", variable=self.type_var).grid(row=0, column=1)
        ttk.Radiobutton(form_frame, text="Expense", value="Expense", variable=self.type_var).grid(row=0, column=2)

        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.date_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Category:").grid(row=3, column=0, padx=5, pady=5)
        self.category_cb = ttk.Combobox(form_frame, state="readonly")
        self.category_cb.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Note:").grid(row=4, column=0, padx=5, pady=5)
        self.note_entry = ttk.Entry(form_frame)
        self.note_entry.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5)

        btn_save = ttk.Button(form_frame, text="Save Transaction", command=self.save_transaction)
        btn_save.grid(row=5, column=0, columnspan=3, pady=10)

        bar = ttk.Frame(self.tab_transactions)
        bar.pack(fill="x", padx=10, pady=2)
        ttk.Label(bar, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(bar, width=18)
        self.search_entry.pack(side="left", padx=4)
        ttk.Label(bar, text="Type:").pack(side="left")
        self.filter_type = ttk.Combobox(bar, values=["All", "Income", "Expense"], state="readonly", width=9)
        self.filter_type.set("All")
        self.filter_type.pack(side="left", padx=4)
        ttk.Label(bar, text="Category:").pack(side="left")
        self.filter_cat = ttk.Combobox(bar, values=["All"], state="readonly", width=14)
        self.filter_cat.set("All")
        self.filter_cat.pack(side="left", padx=4)
        ttk.Button(bar, text="Apply", command=self.apply_filters).pack(side="left", padx=2)
        ttk.Button(bar, text="Clear", command=self.clear_filters).pack(side="left", padx=2)
        ttk.Button(bar, text="Delete Selected", command=self.delete_selected).pack(side="right")

        tree_frame = ttk.Frame(self.tab_transactions)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Date", "Type", "Category", "Amount", "Note")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)

        self.tree.pack(fill="both", expand=True)

    def setup_budgets_tab(self) -> None:
        frame = ttk.LabelFrame(self.tab_budgets, text="Category Budget Limits")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.b_category_cb = ttk.Combobox(frame, state="readonly")
        self.b_category_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Monthly Limit:").grid(row=1, column=0, padx=5, pady=5)
        self.b_limit_entry = ttk.Entry(frame)
        self.b_limit_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_set_budget = ttk.Button(frame, text="Set Budget", command=self.set_budget)
        btn_set_budget.grid(row=2, column=0, columnspan=2, pady=10)

        budget_frame = ttk.Frame(self.tab_budgets)
        budget_frame.pack(fill="both", expand=True, padx=10, pady=5)

        b_columns = ("Category", "Limit", "Spent", "Remaining", "Status")
        self.budget_tree = ttk.Treeview(budget_frame, columns=b_columns, show="headings")
        for col in b_columns:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=110)
        self.budget_tree.tag_configure("over", foreground="red")
        self.budget_tree.pack(fill="both", expand=True)

    def setup_categories_tab(self) -> None:
        frame = ttk.LabelFrame(self.tab_categories, text="Manage Categories")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Category Name:").grid(row=0, column=0, padx=5, pady=5)
        self.cat_entry = ttk.Entry(frame)
        self.cat_entry.grid(row=0, column=1, padx=5, pady=5)

        btn_add_cat = ttk.Button(frame, text="Add Category", command=self.add_category)
        btn_add_cat.grid(row=1, column=0, columnspan=2, pady=10)

        cat_frame = ttk.Frame(self.tab_categories)
        cat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.cat_listbox = tk.Listbox(cat_frame)
        self.cat_listbox.pack(fill="both", expand=True)

    def add_category(self) -> None:
        try:
            self.manager.add_category(self.cat_entry.get().strip())
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return
        self.cat_entry.delete(0, tk.END)
        self.refresh_all_data()

    def set_budget(self) -> None:
        month = datetime.date.today().strftime("%Y-%m")
        try:
            self.manager.add_budget(self.b_category_cb.get(), self.b_limit_entry.get(), month)
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Budget Set", f"Budget saved for {month}.")
        self.b_limit_entry.delete(0, tk.END)
        self.b_category_cb.set("")
        self.refresh_all_data()

    def save_transaction(self) -> None:
        try:
            self.manager.add_transaction(
                self.type_var.get(),
                self.amount_entry.get(),
                self.date_entry.get(),
                self.category_cb.get(),
                self.note_entry.get()
            )
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return

        messagebox.showinfo("Success", "Transaction saved successfully.")
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.category_cb.set("")
        self.note_entry.delete(0, tk.END)
        self.refresh_all_data()

    def apply_filters(self) -> None:
        tx_type = None if self.filter_type.get() in ("", "All") else self.filter_type.get()
        category = None if self.filter_cat.get() in ("", "All") else self.filter_cat.get()
        results = self.manager.filter(category=category, tx_type=tx_type)
        text = self.search_entry.get().strip()
        if text:
            matching_ids = {tx.id for tx in self.manager.search(text)}
            results = [tx for tx in results if tx.id in matching_ids]
        self._fill_table(results)

    def clear_filters(self) -> None:
        self.search_entry.delete(0, tk.END)
        self.filter_type.set("All")
        self.filter_cat.set("All")
        self.refresh_all_data()

    def delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a row first.")
            return
        tx_id = int(self.tree.item(selected[0])["values"][0])
        if not messagebox.askyesno("Confirm", f"Delete transaction {tx_id}?"):
            return
        try:
            self.manager.delete_transaction(tx_id)
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return
        self.refresh_all_data()

    def refresh_all_data(self) -> None:
        transactions = self.manager.get_transactions()
        self._fill_table(transactions)
        
        names = [c.name for c in self.manager.get_categories()]
        self.category_cb["values"] = names
        self.b_category_cb["values"] = names
        self.filter_cat["values"] = ["All"] + names
        
        self.cat_listbox.delete(0, tk.END)
        for name in names:
            self.cat_listbox.insert(tk.END, name)
            
        self._refresh_dashboard(transactions)
        self._refresh_budgets()

    def _fill_table(self, transactions) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for tx in transactions:
            self.tree.insert("", "end", values=(
                tx.id, tx.date, tx.label(), tx.category, f"{tx.amount:.2f}", tx.note
            ))

    def _refresh_dashboard(self, transactions) -> None:
        data = self.manager.dashboard_data()
        self.lbl_income.config(text=f"Total Income: ${data['total_income']:.2f}")
        self.lbl_expense.config(text=f"Total Expenses: ${data['total_expenses']:.2f}")
        self.lbl_balance.config(text=f"Net Balance: ${data['balance']:.2f}")

        spending = {}
        for tx in transactions:
            if tx.label() == "Expense":
                spending[tx.category] = spending.get(tx.category, 0) + tx.amount

        self.ax1.clear()
        self.ax2.clear()

        if spending:
            self.ax1.pie(spending.values(), labels=spending.keys(), autopct="%1.1f%%", startangle=140)
        else:
            self.ax1.text(0.5, 0.5, "No Expense Data", ha="center", va="center")
        self.ax1.set_title("Expenses by Category")

        self.ax2.bar(["Income", "Expense"], [data["total_income"], data["total_expenses"]], color=["green", "red"])
        self.ax2.set_title("Income vs Expenses")
        self.ax2.set_ylabel("Amount ($)")

        self.figure.tight_layout()
        self.canvas.draw()

    def _refresh_budgets(self) -> None:
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        month = datetime.date.today().strftime("%Y-%m")
        for b in self.manager.budget_status(month):
            status = "EXCEEDED" if b["exceeded"] else "OK"
            self.budget_tree.insert("", "end", tags=("over",) if b["exceeded"] else (), values=(
                b["category"], f"{b['limit']:.2f}", f"{b['spent']:.2f}", f"{b['remaining']:.2f}", status
            ))


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()