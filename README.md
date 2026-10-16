# Personal Finance Management System - Student B Sara Laithy

## Overview
This document outlines the specific tasks, responsibilities, and deliverables assigned to **Student B** for the Personal Finance Management System project. The project follows a modular object-oriented programming (OOP) structure in Python, utilizing `tkinter` for the graphical user interface and backend services for data management.

## Student B Sara Laithy Responsibilities & Tasks
- **GUI Development (`GUI/app.py`):**
  - Designed and structured the desktop application using `tkinter` and `ttk`.
  - Implemented multi-tab navigation (`Notebook`) containing Dashboard, Transactions, Budgets, and Categories tabs.
  - Developed form inputs, entry fields, comboboxes, and tables (`Treeview`) for seamless user interaction.
- **Backend Integration:**
  - Linked the graphical interface components to the core backend managers (`FinanceManager` and `FileManager`) to ensure reliable data flow and persistence.
  - Implemented automated data refresh mechanisms for real-time calculation and display of summaries.
- **Testing & Verification:**
  - Verified user data flow across all system modules.
  - Handled exception management for user inputs and data rendering.

## Project Structure
```text
OOP_Python_Project/
├── GUI/
│   └── app.py
├── services/
│   └── finance_manager.py
├── Data/
│   └── file_manager.py
├── Test/
│   └── test_services.py
└── README.md
