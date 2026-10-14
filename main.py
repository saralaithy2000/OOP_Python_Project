"""Entry point: python main.py  (run from the project root)."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from exceptions import FinanceError
from file_manager.file_manager import FileManager
from GUI.app import FinanceApp
from services.finance_manager import FinanceManager


def main() -> None:
    root = tk.Tk()
    try:
        manager = FinanceManager(FileManager("data"))       # loads the JSON files
    except FinanceError as error:
        messagebox.showerror("Cannot start", f"The data files could not be loaded:\n{error}")
        root.destroy()
        return

    def on_close() -> None:
        """Save everything one last time, then close the window."""
        try:
            manager.save_data()
        except FinanceError as error:
            messagebox.showerror("Save failed", str(error))
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    FinanceApp(root, manager)
    root.mainloop()


if __name__ == "__main__":
    main()
