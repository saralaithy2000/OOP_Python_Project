import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#Hi
print("Hi")
try:
    from services.finance_manager import FinanceManager
    from Data.file_manager import FileManager
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False


class DummyFileManager:
    def load_data(self):
        return {"transactions": [], "budgets": {}, "categories": ["Salary", "Food", "Transport", "Rent", "Entertainment"]}

    def save_data(self, data):
        pass


class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Management System")
        self.root.geometry("950x750")

        if HAS_BACKEND:
            try:
                self.manager = FinanceManager(FileManager())
            except Exception:
                self.manager = FinanceManager(DummyFileManager())
        else:
            class LocalManager:
                def __init__(self):
                    self.transactions = []
                    self.categories = ["Salary", "Food", "Transport", "Rent", "Entertainment"]
                def add_transaction(self, tx_type, category, amount, date, note):
                    self.transactions.append({
                        "id": len(self.transactions) + 1,
                        "type": tx_type,
                        "category": category,
                        "amount": amount,
                        "date": date,
                        "note": note
                    })
                def get_all_transactions(self):
                    return self.transactions
                def get_categories(self):
                    return self.categories
                def add_category(self, name):
                    if name not in self.categories:
                        self.categories.append(name)
                def get_summary(self):
                    inc = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
                    exp = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
                    return inc, exp, inc - exp
            self.manager = LocalManager()

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

    def setup_dashboard_tab(self):
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

    def setup_transactions_tab(self):
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
        self.date_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Category:").grid(row=3, column=0, padx=5, pady=5)
        self.category_cb = ttk.Combobox(form_frame)
        self.category_cb.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)

        ttk.Label(form_frame, text="Note:").grid(row=4, column=0, padx=5, pady=5)
        self.note_entry = ttk.Entry(form_frame)
        self.note_entry.grid(row=4, column=1, columnspan=2, sticky="ew", padx=5)

        btn_save = ttk.Button(form_frame, text="Save Transaction", command=self.save_transaction)
        btn_save.grid(row=5, column=0, columnspan=3, pady=10)

        tree_frame = ttk.Frame(self.tab_transactions)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Date", "Type", "Category", "Amount", "Note")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)

        self.tree.pack(fill="both", expand=True)

    def setup_budgets_tab(self):
        frame = ttk.LabelFrame(self.tab_budgets, text="Category Budget Limits")
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="Category:").grid(row=0, column=0, padx=5, pady=5)
        self.b_category_cb = ttk.Combobox(frame)
        self.b_category_cb.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Monthly Limit:").grid(row=1, column=0, padx=5, pady=5)
        self.b_limit_entry = ttk.Entry(frame)
        self.b_limit_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_set_budget = ttk.Button(frame, text="Set Budget", command=self.set_budget)
        btn_set_budget.grid(row=2, column=0, columnspan=2, pady=10)

    def setup_categories_tab(self):
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

    def add_category(self):
        cat_name = self.cat_entry.get().strip()
        if cat_name:
            try:
                if hasattr(self.manager, "add_category"):
                    self.manager.add_category(cat_name)
                elif hasattr(self.manager, "categories"):
                    if cat_name not in self.manager.categories:
                        self.manager.categories.append(cat_name)
            except Exception:
                pass

            messagebox.showinfo("Success", f"Category '{cat_name}' added successfully.")
            self.cat_entry.delete(0, tk.END)
            self.refresh_all_data()
        else:
            messagebox.showerror("Error", "Please enter a category name.")

    def set_budget(self):
        cat = self.b_category_cb.get()
        limit = self.b_limit_entry.get()
        if cat and limit:
            messagebox.showinfo("Budget Set", f"Budget limit of ${limit} set for {cat}.")
            self.b_limit_entry.delete(0, tk.END)
            self.b_category_cb.set("")
        else:
            messagebox.showerror("Error", "Please fill category and limit.")

    def save_transaction(self):
        tx_type = self.type_var.get()
        amount = self.amount_entry.get()
        date = self.date_entry.get()
        category = self.category_cb.get()
        note = self.note_entry.get()

        if not amount or not date or not category:
            messagebox.showerror("Error", "Please fill all required fields.")
            return

        try:
            float_amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number.")
            return

        try:
            self.manager.add_transaction(tx_type, category, float_amount, date, note)
        except TypeError:
            try:
                self.manager.add_transaction(amount=float_amount, category=category, date=date, transaction_type=tx_type, note=note)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
                return

        messagebox.showinfo("Success", "Transaction saved successfully.")

        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.category_cb.set("")
        self.note_entry.delete(0, tk.END)

        self.refresh_all_data()

    def refresh_all_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            transactions = self.manager.get_all_transactions()
        except AttributeError:
            try:
                transactions = self.manager.transactions
            except:
                transactions = []

        if transactions:
            for tx in transactions:
                if isinstance(tx, dict):
                    self.tree.insert("", "end", values=(
                        tx.get("id", "-"),
                    tx.get("date", "-"),
                        tx.get("type", "-"),
                        tx.get("category", "-"),
                        f"${tx.get('amount', 0):.2f}",
                        tx.get("note", "")
                    ))
                else:
                    self.tree.insert("", "end", values=(
                        getattr(tx, "id", "-"),
                        getattr(tx, "date", "-"),
                        getattr(tx, "type", "-"),
                        getattr(tx, "category", "-"),
                        f"${getattr(tx, 'amount', 0):.2f}",
                        getattr(tx, "note", "")
                    ))

        try:
            categories = []
            if hasattr(self.manager, "get_categories"):
                categories = self.manager.get_categories()
            elif hasattr(self.manager, "categories"):
                categories = self.manager.categories
            else:
                categories = ["Salary", "Food", "Transport", "Rent", "Entertainment"]

            self.category_cb["values"] = categories
            self.b_category_cb["values"] = categories

            self.cat_listbox.delete(0, tk.END)
            for cat in categories:
                self.cat_listbox.insert(tk.END, cat)
        except:
            pass

        try:
            income, expense, balance = self.manager.get_summary()
            self.lbl_income.config(text=f"Total Income: ${income:.2f}")
            self.lbl_expense.config(text=f"Total Expenses: ${expense:.2f}")
            self.lbl_balance.config(text=f"Net Balance: ${balance:.2f}")

            self.ax1.clear()
            self.ax2.clear()

            # Pie Chart (Expenses by Category)
            expense_categories = {}
            for tx in transactions:
                t_type = tx.get("type") if isinstance(tx, dict) else getattr(tx, "type", "")
                t_cat = tx.get("category") if isinstance(tx, dict) else getattr(tx, "category", "")
                t_amt = tx.get("amount") if isinstance(tx, dict) else getattr(tx, "amount", 0)
                if t_type == "Expense":
                    expense_categories[t_cat] = expense_categories.get(t_cat, 0) + float(t_amt)

            if expense_categories:
                self.ax1.pie(expense_categories.values(), labels=expense_categories.keys(), autopct='%1.1f%%', startangle=140)
                self.ax1.set_title("Expenses by Category")
            else:
                self.ax1.text(0.5, 0.5, "No Expense Data", horizontalalignment='center', verticalalignment='center')
                self.ax1.set_title("Expenses by Category")

            # Bar Chart (Income vs Expenses)
            self.ax2.bar(["Income", "Expense"], [income, expense], color=["green", "red"])
            self.ax2.set_title("Income vs Expenses")
            self.ax2.set_ylabel("Amount ($)")

            self.figure.tight_layout()
            self.canvas.draw()
        except Exception:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()