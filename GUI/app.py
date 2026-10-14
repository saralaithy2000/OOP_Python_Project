import tkinter as tk
from tkinter import ttk, messagebox

class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Management System")
        self.root.geometry("800x600")

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

        self.setup_transactions_tab()

    def setup_transactions_tab(self):
        form_frame = ttk.LabelFrame(self.tab_transactions, text="Add Transaction")
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
        self.category_cb = ttk.Combobox(form_frame, values=["Salary", "Food", "Transport", "Rent", "Entertainment"])
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
            self.tree.column(col, width=100)
        
        self.tree.pack(fill="both", expand=True)

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

        self.tree.insert("", "end", values=("1", date, tx_type, category, float_amount, note))
        messagebox.showinfo("Success", "Transaction added successfully.")
        
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.category_cb.set("")
        self.note_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()