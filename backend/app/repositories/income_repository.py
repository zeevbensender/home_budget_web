"""Repository for Income model data access operations."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.income import Income
from app.repositories.base_repository import BaseRepository


class IncomeRepository(BaseRepository[Income]):
    """
    Repository for managing Income records in the database.

    Provides CRUD operations and income-specific query methods
    beyond the base repository functionality.

    Example:
        >>> from app.core.database import SessionLocal
        >>> db = SessionLocal()
        >>> repo = IncomeRepository(db)
        >>> income = repo.create(
        ...     date=date(2025, 12, 1),
        ...     category="Salary",
        ...     amount=Decimal("5000.00"),
        ...     account="Bank Account",
        ...     currency="₪"
        ... )
        >>> print(income.id)
        1
    """

    def __init__(self, db: Session):
        """Initialize the income repository with a database session."""
        super().__init__(Income, db)

    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> List[Income]:
        """
        Get all income records within a date range.

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            List of income records in the date range, ordered by date descending
        """
        return (
            self.db.query(Income)
            .filter(Income.date >= start_date)
            .filter(Income.date <= end_date)
            .order_by(Income.date.desc())
            .all()
        )

    def get_by_category(self, category: str) -> List[Income]:
        """
        Get all income records for a specific category.

        Args:
            category: The category name to filter by

        Returns:
            List of income records in the category, ordered by date descending
        """
        return (
            self.db.query(Income)
            .filter(Income.category == category)
            .order_by(Income.date.desc())
            .all()
        )

    def get_by_account(self, account: str) -> List[Income]:
        """
        Get all income records for a specific account.

        Args:
            account: The account name to filter by

        Returns:
            List of income records for the account, ordered by date descending
        """
        return (
            self.db.query(Income)
            .filter(Income.account == account)
            .order_by(Income.date.desc())
            .all()
        )

    def get_total_by_category(self, category: str) -> Decimal:
        """
        Calculate total income amount in a specific category.

        Args:
            category: The category name to sum

        Returns:
            Total amount as Decimal, or Decimal("0") if no income
        """
        result = (
            self.db.query(func.sum(Income.amount))
            .filter(Income.category == category)
            .scalar()
        )
        return result if result is not None else Decimal("0")

    def get_total_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """
        Calculate total income within a date range.

        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)

        Returns:
            Total amount as Decimal, or Decimal("0") if no income
        """
        result = (
            self.db.query(func.sum(Income.amount))
            .filter(Income.date >= start_date)
            .filter(Income.date <= end_date)
            .scalar()
        )
        return result if result is not None else Decimal("0")

    def get_all_categories(self) -> List[str]:
        """
        Get list of all unique income categories.

        Returns:
            List of category names, sorted alphabetically
        """
        categories = (
            self.db.query(Income.category)
            .distinct()
            .order_by(Income.category)
            .all()
        )
        return [cat[0] for cat in categories]

    def get_all_accounts(self) -> List[str]:
        """
        Get list of all unique accounts that received income.

        Returns:
            List of account names, sorted alphabetically
        """
        accounts = (
            self.db.query(Income.account)
            .distinct()
            .order_by(Income.account)
            .all()
        )
        return [acc[0] for acc in accounts]

    def get_recent(self, limit: int = 10) -> List[Income]:
        """
        Get the most recent income records.

        Args:
            limit: Maximum number of income records to return (default: 10)

        Returns:
            List of most recent income records, ordered by date descending
        """
        return (
            self.db.query(Income)
            .order_by(Income.date.desc())
            .limit(limit)
            .all()
        )
