"""Tkinter interface for the Personal Finance Management System.

Start the program with:  python main.py   (main.py loads the data and opens this window)
"""
from __future__ import annotations

import datetime
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from exceptions import FinanceError  # noqa: E402
from services.finance_manager import FinanceManager  # noqa: E402


class FinanceApp:
    def __init__(self, root: tk.Tk, manager: FinanceManager) -> None:
        self.root = root
        self.manager = manager
        self.editing_id: int | None = None      # ID of the transaction being edited, or None

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
        self.form_frame = form_frame

        ttk.Label(form_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar(value="Expense")
        self.rb_income = ttk.Radiobutton(form_frame, text="Income", value="Income", variable=self.type_var)
        self.rb_income.grid(row=0, column=1)
        self.rb_expense = ttk.Radiobutton(form_frame, text="Expense", value="Expense", variable=self.type_var)
        self.rb_expense.grid(row=0, column=2)

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

        self.btn_save = ttk.Button(form_frame, text="Save Transaction", command=self.save_transaction)
        self.btn_save.grid(row=5, column=0, columnspan=2, pady=10)
        self.btn_cancel_edit = ttk.Button(form_frame, text="Cancel Edit", command=self.cancel_edit)
        self.btn_cancel_edit.grid(row=5, column=2, pady=10)
        self.btn_cancel_edit.grid_remove()          # only visible while editing

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
        ttk.Button(bar, text="Edit Selected", command=self.edit_selected).pack(side="right", padx=4)

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

        month = datetime.date.today().strftime("%Y-%m")
        ttk.Label(self.tab_budgets, text=f"Budgets for the current month ({month})").pack(anchor="w", padx=10)
        budget_frame = ttk.Frame(self.tab_budgets)
        budget_frame.pack(fill="both", expand=True, padx=10, pady=5)

        b_columns = ("Category", "Limit", "Spent", "Remaining", "Status")
        self.budget_tree = ttk.Treeview(budget_frame, columns=b_columns, show="headings")
        for col in b_columns:
            self.budget_tree.heading(col, text=col)
            self.budget_tree.column(col, width=110)
        self.budget_tree.tag_configure("over", foreground="red")
        self.budget_tree.pack(fill="both", expand=True)

        ttk.Button(self.tab_budgets, text="Delete Selected Budget", command=self.delete_budget).pack(pady=5)

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
        """Create the budget, or replace it if one already exists for this category and month."""
        month = datetime.date.today().strftime("%Y-%m")
        category = self.b_category_cb.get()
        old = next((b for b in self.manager.get_budgets()
                    if b.category.lower() == category.lower() and b.month == month), None)
        if old is not None and not messagebox.askyesno(
                "Replace budget", f"{old.category} already has a budget of {old.limit:.2f} for {month}.\nReplace it?"):
            return
        try:
            if old is not None:
                self.manager.delete_budget(old.category, month)
            try:
                self.manager.add_budget(category, self.b_limit_entry.get(), month)
            except FinanceError:
                if old is not None:                      # the new value was invalid: put the old budget back
                    self.manager.add_budget(old.category, old.limit, old.month)
                raise
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Budget Set", f"Budget saved for {month}.")
        self.b_limit_entry.delete(0, tk.END)
        self.b_category_cb.set("")
        self.refresh_all_data()

    def delete_budget(self) -> None:
        selected = self.budget_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a budget row first.")
            return
        category = str(self.budget_tree.item(selected[0])["values"][0])
        month = datetime.date.today().strftime("%Y-%m")
        if not messagebox.askyesno("Confirm", f"Delete the {category} budget for {month}?"):
            return
        try:
            self.manager.delete_budget(category, month)
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return
        self.refresh_all_data()

    def save_transaction(self) -> None:
        """Add a new transaction, or save the changes if one is being edited."""
        try:
            if self.editing_id is None:
                self.manager.add_transaction(
                    self.type_var.get(),
                    self.amount_entry.get(),
                    self.date_entry.get(),
                    self.category_cb.get(),
                    self.note_entry.get()
                )
                message = "Transaction saved successfully."
            else:
                self.manager.update_transaction(
                    self.editing_id,
                    amount=self.amount_entry.get(),
                    date=self.date_entry.get(),
                    category=self.category_cb.get(),
                    note=self.note_entry.get()
                )
                message = "Transaction updated successfully."
        except FinanceError as error:
            messagebox.showerror("Error", str(error))
            return

        messagebox.showinfo("Success", message)
        self._reset_form()
        self.refresh_all_data()

    def edit_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a row first.")
            return
        tx_id = int(self.tree.item(selected[0])["values"][0])
        tx = next((t for t in self.manager.get_transactions() if t.id == tx_id), None)
        if tx is None:
            messagebox.showerror("Error", f"Transaction {tx_id} no longer exists.")
            return
        self.editing_id = tx_id
        self.type_var.set(tx.label())
        self.rb_income.state(["disabled"])              # the type of a transaction cannot be changed
        self.rb_expense.state(["disabled"])
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, str(tx.amount))
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, tx.date)
        self.category_cb.set(tx.category)
        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, tx.note)
        self.form_frame.config(text=f"Edit Transaction {tx_id}")
        self.btn_save.config(text="Update Transaction")
        self.btn_cancel_edit.grid()
        self.amount_entry.focus_set()

    def cancel_edit(self) -> None:
        self._reset_form()

    def _reset_form(self) -> None:
        """Clear the form and go back to 'add new transaction' mode."""
        self.editing_id = None
        self.rb_income.state(["!disabled"])
        self.rb_expense.state(["!disabled"])
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().isoformat())
        self.category_cb.set("")
        self.note_entry.delete(0, tk.END)
        self.form_frame.config(text="Add New Transaction")
        self.btn_save.config(text="Save Transaction")
        self.btn_cancel_edit.grid_remove()

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
        if self.editing_id == tx_id:
            self._reset_form()
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
    from main import main      # same start-up (with error boxes) as python main.py
    main()
