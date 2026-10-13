"""Custom exceptions for the Personal Finance application."""


class FinanceError(Exception):
    """Base class for every error this application raises on purpose."""


class ValidationError(FinanceError):
    """Raised when a value breaks a rule (negative amount, bad date, empty name...)."""


class NotFoundError(FinanceError):
    """Raised when we look for something (a transaction, an account) that does not exist."""


class BudgetError(FinanceError):
    """Raised when a budget rule is broken."""


class DataFileError(FinanceError):
    """Raised when a data file is missing its content, unreadable or corrupted."""
