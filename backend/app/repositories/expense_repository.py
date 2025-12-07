"""Repository for Expense model data access operations."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories.base_repository import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """
    Repository for managing Expense records in the database.

    Provides CRUD operations and expense-specific query methods
    beyond the base repository functionality.

    Example:
        >>> from app.core.database import SessionLocal
        >>> db = SessionLocal()
        >>> repo = ExpenseRepository(db)
        >>> expense = repo.create(
        ...     date=date(2025, 12, 1),
        ...     category="Groceries",
        ...     amount=Decimal("142.50"),
        ...     account="Visa",
        ...     currency="₪"
        ... )
        >>> print(expense.id)
        1
    """

    def __init__(self, db: Session):
        """Initialize the expense repository with a database session."""
        super().__init__(Expense, db)

    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> List[Expense]:
        """
        Get all expenses within a date range.

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of expenses in the date range, ordered by date descending
        """
        return (
            self.db.query(Expense)
            .filter(Expense.date >= start_date)
            .filter(Expense.date <= end_date)
            .order_by(Expense.date.desc())
            .all()
        )

    def get_by_category(self, category: str) -> List[Expense]:
        """
        Get all expenses for a specific category.

        Args:
            category: The category name to filter by

        Returns:
            List of expenses in the category, ordered by date descending
        """
        return (
            self.db.query(Expense)
            .filter(Expense.category == category)
            .order_by(Expense.date.desc())
            .all()
        )

    def get_by_account(self, account: str) -> List[Expense]:
        """
        Get all expenses for a specific account.

        Args:
            account: The account name to filter by

        Returns:
            List of expenses for the account, ordered by date descending
        """
        return (
            self.db.query(Expense)
            .filter(Expense.account == account)
            .order_by(Expense.date.desc())
            .all()
        )

    def get_total_by_category(self, category: str) -> Decimal:
        """
        Calculate total amount spent in a specific category.

        Args:
            category: The category name to sum

        Returns:
            Total amount as Decimal, or Decimal("0") if no expenses
        """
        result = (
            self.db.query(func.sum(Expense.amount))
            .filter(Expense.category == category)
            .scalar()
        )
        return result if result is not None else Decimal("0")

    def get_total_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """
        Calculate total expenses within a date range.

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            Total amount as Decimal, or Decimal("0") if no expenses
        """
        result = (
            self.db.query(func.sum(Expense.amount))
            .filter(Expense.date >= start_date)
            .filter(Expense.date <= end_date)
            .scalar()
        )
        return result if result is not None else Decimal("0")

    def get_all_categories(self) -> List[str]:
        """
        Get list of all unique expense categories.

        Returns:
            List of category names, sorted alphabetically
        """
        categories = (
            self.db.query(Expense.category)
            .distinct()
            .order_by(Expense.category)
            .all()
        )
        return [cat[0] for cat in categories]

    def get_all_accounts(self) -> List[str]:
        """
        Get list of all unique accounts used for expenses.

        Returns:
            List of account names, sorted alphabetically
        """
        accounts = (
            self.db.query(Expense.account)
            .distinct()
            .order_by(Expense.account)
            .all()
        )
        return [acc[0] for acc in accounts]

    def search_by_business(self, business_name: str) -> List[Expense]:
        """
        Search expenses by business name (case-insensitive partial match).

        Args:
            business_name: Business name or partial name to search for

        Returns:
            List of matching expenses, ordered by date descending
        """
        return (
            self.db.query(Expense)
            .filter(Expense.business.ilike(f"%{business_name}%"))
            .order_by(Expense.date.desc())
            .all()
        )

    def get_recent(self, limit: int = 10) -> List[Expense]:
        """
        Get the most recent expenses.

        Args:
            limit: Maximum number of expenses to return (default: 10)

        Returns:
            List of most recent expenses, ordered by date descending
        """
        return (
            self.db.query(Expense)
            .order_by(Expense.date.desc())
            .limit(limit)
            .all()
        )
