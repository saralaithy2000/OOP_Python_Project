# UML class diagrams

These diagrams use [Mermaid](https://mermaid.js.org/), which GitHub renders automatically when you open this file. To get a picture for a report or slides, paste a diagram into <https://mermaid.live> and export it as PNG or SVG.

## 1. Main class diagram

```mermaid
classDiagram
    direction TB

    class Transaction {
        <<abstract>>
        -int _id
        -float _amount
        -str _date
        -str _category
        -str _note
        +int id
        +float amount
        +str date
        +str category
        +str note
        +signed_amount() float*
        +label() str*
        +to_dict() dict
        +from_dict(dict data) Transaction$
    }
    class Income {
        -str _source
        +str source
        +signed_amount() float
        +label() str
        +to_dict() dict
    }
    class Expense {
        -str _payment_method
        +str payment_method
        +signed_amount() float
        +label() str
        +to_dict() dict
    }
    class Category {
        -int _id
        -str _name
        -str _kind
        +int id
        +str name
        +str kind
        +to_dict() dict
        +from_dict(dict data) Category$
    }
    class Budget {
        -str _category
        -float _limit
        -str _month
        +str category
        +float limit
        +str month
        +spent(list transactions) float
        +remaining(list transactions) float
        +is_exceeded(list transactions) bool
        +to_dict() dict
        +from_dict(dict data) Budget$
    }
    class Account {
        -str _name
        -float _opening_balance
        -list _transactions
        +str name
        +float opening_balance
        +list transactions
        +add_transaction(Transaction tx)
        +find_by_id(int tx_id) Transaction
        +remove_transaction(int tx_id)
        +balance() float
    }
    class User {
        -str _name
        -list _accounts
        +str name
        +list accounts
        +add_account(Account account)
        +get_account(str name) Account
    }
    class FileManager {
        -Path _data_dir
        -_read_json(str filename, list default) list
        -_write_json(str filename, list records)
        +load_transactions() list
        +save_transactions(list transactions)
        +load_categories() list
        +save_categories(list categories)
        +load_budgets() list
        +save_budgets(list budgets)
    }
    class FinanceManager {
        -FileManager _file_manager
        -User _user
        -Account _account
        -list _categories
        -list _budgets
        +load_data()
        +save_data()
        +add_transaction(...) Transaction
        +update_transaction(int tx_id, ...) Transaction
        +delete_transaction(int tx_id)
        +get_transactions() list
        +search(str text) list
        +filter(...) list
        +get_categories() list
        +add_category(str name, str kind) Category
        +delete_category(str name)
        +get_budgets() list
        +add_budget(str category, float limit, str month) Budget
        +delete_budget(str category, str month)
        +monthly_summary(int year, int month) dict
        +budget_status(str month) list
        +dashboard_data() dict
    }
    class FinanceApp {
        <<GUI>>
        -Tk root
        -FinanceManager manager
        +setup_dashboard_tab()
        +setup_transactions_tab()
        +setup_budgets_tab()
        +setup_categories_tab()
        +save_transaction()
        +apply_filters()
        +delete_selected()
        +set_budget()
        +add_category()
        +refresh_all_data()
    }

    Transaction <|-- Income : inherits
    Transaction <|-- Expense : inherits
    User "1" *-- "1..*" Account : owns
    Account "1" *-- "0..*" Transaction : contains
    FinanceManager "1" *-- "1" User : has
    FinanceManager "1" o-- "1" Account : main account
    FinanceManager "1" o-- "0..*" Category : manages
    FinanceManager "1" o-- "0..*" Budget : manages
    FinanceManager "1" --> "1" FileManager : uses
    FinanceApp "1" --> "1" FinanceManager : calls
    FileManager ..> Transaction : loads / saves
    FileManager ..> Category : loads / saves
    FileManager ..> Budget : loads / saves
    Budget ..> Expense : adds up spending
```

## 2. Exception hierarchy

```mermaid
classDiagram
    direction TB
    class Exception
    class FinanceError
    class ValidationError
    class NotFoundError
    class BudgetError
    class DataFileError
    Exception <|-- FinanceError
    FinanceError <|-- ValidationError
    FinanceError <|-- NotFoundError
    FinanceError <|-- BudgetError
    FinanceError <|-- DataFileError
    note for FinanceError "Base class for every error the app raises on purpose"
    note for ValidationError "A value breaks a rule"
    note for NotFoundError "A transaction, account or budget does not exist"
    note for BudgetError "A budget rule is broken"
    note for DataFileError "A data file is unreadable or corrupted"
```

## 3. Layers

```mermaid
flowchart LR
    GUI["GUI<br/>FinanceApp"] --> SVC["Service<br/>FinanceManager"]
    SVC --> MOD["Models<br/>Transaction, Income, Expense,<br/>Category, Budget, Account, User"]
    SVC --> FM["FileManager"]
    FM --> JSON[("JSON files<br/>data/")]
```

## Legend

| Symbol | Meaning |
|---|---|
| `<\|--` | inheritance (`Income` is a `Transaction`) |
| `*--` | composition (the part cannot live without the whole) |
| `o--` | aggregation (the manager holds the object) |
| `-->` | association (uses) |
| `..>` | dependency |
| `-` / `+` | private / public member |
| `*` after a method | abstract method |
| `$` after a method | static method |
