"""Storage factory for switching between JSON and PostgreSQL storage."""

from app.core.settings import get_storage_type
from app.core.expense_repository import (
    ExpenseRepositoryInterface,
    JsonExpenseRepository,
    PostgresExpenseRepository,
)
from app.core.income_repository import (
    IncomeRepositoryInterface,
    JsonIncomeRepository,
    PostgresIncomeRepository,
)

# Singleton instances for repositories
_expense_repository: ExpenseRepositoryInterface = None
_income_repository: IncomeRepositoryInterface = None


def get_expense_repository() -> ExpenseRepositoryInterface:
    """Get the expense repository based on storage type."""
    global _expense_repository
    if _expense_repository is None:
        storage_type = get_storage_type()
        if storage_type == "postgres":
            from app.core.db import create_tables
            create_tables()
            _expense_repository = PostgresExpenseRepository()
        else:
            from app.core import storage
            _expense_repository = JsonExpenseRepository(storage)
    return _expense_repository


def get_income_repository() -> IncomeRepositoryInterface:
    """Get the income repository based on storage type."""
    global _income_repository
    if _income_repository is None:
        storage_type = get_storage_type()
        if storage_type == "postgres":
            from app.core.db import create_tables
            create_tables()
            _income_repository = PostgresIncomeRepository()
        else:
            from app.core import storage
            _income_repository = JsonIncomeRepository(storage)
    return _income_repository


def reset_repositories():
    """Reset repository instances. Useful for testing."""
    global _expense_repository, _income_repository
    _expense_repository = None
    _income_repository = None
