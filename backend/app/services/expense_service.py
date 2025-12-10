"""
Expense service layer for business logic.

This service handles expense-related business logic and data access.
Uses PostgreSQL database as primary storage (Phase 5 - JSON storage removed).
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.feature_flags import is_feature_enabled  # For non-storage features
from app.core.settings import get_default_currency
from app.models.expense import Expense
from app.repositories.expense_repository import ExpenseRepository

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for managing expenses.

    Provides business logic layer between routers and data access.
    Handles data transformation, validation, and storage operations.
    Uses PostgreSQL database as primary storage.
    """

    def __init__(self, db: Session):
        """Initialize expense service.

        Args:
            db: Database session for repository access
        """
        self.db = db
        self.repository = ExpenseRepository(db)

    def _convert_from_db_format(self, expense) -> Dict[str, Any]:
        """Convert SQLAlchemy model instance to dictionary format.

        Args:
            expense: SQLAlchemy Expense model instance

        Returns:
            Dictionary with date as string and amount as float
        """
        # Handle both model instances and dictionaries
        if isinstance(expense, Expense):
            return {
                "id": expense.id,
                "date": expense.date.strftime("%Y-%m-%d"),
                "business": expense.business,
                "category": expense.category,
                "amount": float(expense.amount),
                "account": expense.account,
                "currency": expense.currency,
                "notes": expense.notes,
            }
        return expense

    def list_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses.

        Returns:
            List of expense dictionaries
        """
        expenses = self.repository.list(order_by="-date")
        return [self._convert_from_db_format(e) for e in expenses]

    def get_expense(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Get a single expense by ID.

        Args:
            expense_id: The expense ID

        Returns:
            Expense dictionary if found, None otherwise
        """
        expense = self.repository.get(expense_id)
        return self._convert_from_db_format(expense) if expense else None

    def create_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new expense.

        Args:
            data: Expense data dictionary

        Returns:
            Created expense with assigned ID
        """
        # Auto-fill currency if missing
        if not data.get("currency"):
            data["currency"] = get_default_currency()

        # Create in PostgreSQL database
        created = self.repository.create(data)
        return self._convert_from_db_format(created)

    def update_expense(
        self,
        expense_id: int,
        field: str,
        value: Any,
    ) -> Optional[Dict[str, Any]]:
        """Update a single field of an expense.

        Args:
            expense_id: The expense ID
            field: The field name to update
            value: The new value

        Returns:
            Updated expense if found, None otherwise
        """
        # Get existing expense from database
        existing = self.repository.get(expense_id)
        if not existing:
            return None

        # Handle currency special case
        if field == "currency" and value is None:
            value = get_default_currency()

        # Update in PostgreSQL database
        update_data = {field: value}
        updated = self.repository.update(expense_id, update_data)
        if not updated:
            return None

        return self._convert_from_db_format(updated)

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense.

        Args:
            expense_id: The expense ID to delete

        Returns:
            True if deleted, False if not found
        """
        # Check if exists first
        existing = self.repository.get(expense_id)
        if not existing:
            return False

        # Delete from PostgreSQL database
        return self.repository.delete(expense_id)

    def bulk_delete_expenses(self, ids: List[int]) -> int:
        """Delete multiple expenses.

        Args:
            ids: List of expense IDs to delete

        Returns:
            Number of expenses actually deleted
        """
        # Delete from PostgreSQL database
        return self.repository.bulk_delete(ids)


def format_expense_amount(
    amount: float,
    currency: str,
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> str:
    """
    Format expense amount with currency symbol.

    This demonstrates feature flag usage for a phased rollout of
    a new formatting style.

    Feature flag: EXPENSE_AMOUNT_V2_FORMAT
    - When disabled (default): Returns simple format "142.50 ₪"
    - When enabled: Returns formatted with thousand separators "1,234.50 ₪"

    Args:
        amount: The expense amount
        currency: The currency symbol
        user_id: Optional user ID for per-user flag checks
        db: Optional database session for DB-based flags

    Returns:
        Formatted amount string
    """
    if is_feature_enabled("EXPENSE_AMOUNT_V2_FORMAT", user_id=user_id, db=db):
        # New format with thousand separators (v2)
        return f"{amount:,.2f} {currency}"
    else:
        # Original format (v1)
        return f"{amount:.2f} {currency}"


def get_expense_summary(
    expenses: list[dict[str, Any]],
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """
    Get expense summary with optional enhanced statistics.

    Feature flag: ENHANCED_EXPENSE_STATS
    - When disabled (default): Returns basic summary (total, count)
    - When enabled: Returns enhanced summary (total, count, average, min, max)

    Args:
        expenses: List of expense dictionaries
        user_id: Optional user ID for per-user flag checks
        db: Optional database session for DB-based flags

    Returns:
        Summary dictionary
    """
    if not expenses:
        return {"total": 0, "count": 0}

    amounts = [e.get("amount", 0) for e in expenses]
    total = sum(amounts)
    count = len(amounts)

    summary: dict[str, Any] = {
        "total": round(total, 2),
        "count": count,
    }

    # Enhanced statistics when feature flag is enabled
    if is_feature_enabled("ENHANCED_EXPENSE_STATS", user_id=user_id, db=db):
        summary["average"] = round(total / count, 2) if count > 0 else 0
        summary["min"] = round(min(amounts), 2) if amounts else 0
        summary["max"] = round(max(amounts), 2) if amounts else 0

    return summary
