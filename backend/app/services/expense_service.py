"""
Expense service layer for business logic.

This service handles expense-related business logic and data access.
Phase 2: Uses JSON storage
Phase 3: Adds dual-write to PostgreSQL
Phase 4: Switches to reading from PostgreSQL
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.feature_flags import is_feature_enabled
from app.core.settings import get_default_currency
from app.core.storage import load_json, save_json
from app.repositories.expense_repository import ExpenseRepository

logger = logging.getLogger(__name__)


class ExpenseService:
    """Service for managing expenses.
    
    Provides business logic layer between routers and data access.
    Handles data transformation, validation, and storage operations.
    """
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize expense service.
        
        Args:
            db: Optional database session (for dual-write and repository access)
        """
        self.db = db
        self.repository = ExpenseRepository(db) if db else None
        self._expenses_cache: Optional[List[Dict[str, Any]]] = None
    
    def _load_expenses(self) -> List[Dict[str, Any]]:
        """Load expenses from JSON storage.
        
        Returns:
            List of expense dictionaries
        """
        return load_json("expenses.json", [])
    
    def _save_expenses(self, expenses: List[Dict[str, Any]]) -> None:
        """Save expenses to JSON storage.
        
        Args:
            expenses: List of expense dictionaries to save
        """
        save_json("expenses.json", expenses)
    
    def _convert_to_db_format(self, expense: Dict[str, Any]) -> Dict[str, Any]:
        """Convert expense dict to database format.
        
        Args:
            expense: Expense dictionary
        
        Returns:
            Dictionary formatted for database
        """
        db_data = expense.copy()
        
        # Convert date string to date object if needed
        if isinstance(db_data.get("date"), str):
            db_data["date"] = datetime.strptime(db_data["date"], "%Y-%m-%d").date()
        
        # Convert amount to Decimal if needed
        if isinstance(db_data.get("amount"), (int, float)):
            db_data["amount"] = Decimal(str(db_data["amount"]))
        
        return db_data
    
    def _dual_write_create(self, expense: Dict[str, Any]) -> None:
        """Write expense to database in dual-write mode.
        
        Args:
            expense: Expense dictionary to write
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            db_data = self._convert_to_db_format(expense)
            self.repository.create(db_data)
            logger.info(f"Dual-write: Created expense {expense['id']} in database")
        except Exception as e:
            logger.warning(f"Dual-write failed for expense {expense['id']}: {e}")
    
    def _dual_write_update(self, expense_id: int, data: Dict[str, Any]) -> None:
        """Update expense in database in dual-write mode.
        
        Args:
            expense_id: Expense ID
            data: Updated fields
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            db_data = self._convert_to_db_format(data)
            self.repository.update(expense_id, db_data)
            logger.info(f"Dual-write: Updated expense {expense_id} in database")
        except Exception as e:
            logger.warning(f"Dual-write failed for expense {expense_id}: {e}")
    
    def _dual_write_delete(self, expense_id: int) -> None:
        """Delete expense from database in dual-write mode.
        
        Args:
            expense_id: Expense ID to delete
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            self.repository.delete(expense_id)
            logger.info(f"Dual-write: Deleted expense {expense_id} from database")
        except Exception as e:
            logger.warning(f"Dual-write failed for expense {expense_id}: {e}")
    
    def _dual_write_bulk_delete(self, ids: List[int]) -> None:
        """Bulk delete expenses from database in dual-write mode.
        
        Args:
            ids: List of expense IDs to delete
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            deleted = self.repository.bulk_delete(ids)
            logger.info(f"Dual-write: Bulk deleted {deleted} expenses from database")
        except Exception as e:
            logger.warning(f"Dual-write bulk delete failed: {e}")
    
    def list_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses.
        
        Returns:
            List of expense dictionaries
        """
        return self._load_expenses()
    
    def get_expense(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Get a single expense by ID.
        
        Args:
            expense_id: The expense ID
        
        Returns:
            Expense dictionary if found, None otherwise
        """
        expenses = self._load_expenses()
        for expense in expenses:
            if expense.get("id") == expense_id:
                return expense
        return None
    
    def create_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new expense.
        
        Args:
            data: Expense data dictionary
        
        Returns:
            Created expense with assigned ID
        """
        expenses = self._load_expenses()
        
        # Generate new ID
        new_id = max([e["id"] for e in expenses], default=0) + 1
        
        # Auto-fill currency if missing
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        
        # Create expense record
        expense = {**data, "id": new_id}
        expenses.append(expense)
        
        # Save to JSON (primary storage)
        self._save_expenses(expenses)
        
        # Dual-write to database if enabled
        self._dual_write_create(expense)
        
        return expense
    
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
        expenses = self._load_expenses()
        
        for expense in expenses:
            if expense["id"] == expense_id:
                # Validate field exists
                if field not in expense:
                    raise ValueError(f"Invalid field: {field}")
                
                # Handle currency special case
                if field == "currency" and value is None:
                    expense["currency"] = get_default_currency()
                else:
                    expense[field] = value
                
                # Save to JSON (primary storage)
                self._save_expenses(expenses)
                
                # Dual-write to database if enabled
                self._dual_write_update(expense_id, {field: expense[field]})
                
                return expense
        
        return None
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense.
        
        Args:
            expense_id: The expense ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        expenses = self._load_expenses()
        initial_count = len(expenses)
        
        expenses = [e for e in expenses if e["id"] != expense_id]
        
        if len(expenses) < initial_count:
            # Save to JSON (primary storage)
            self._save_expenses(expenses)
            
            # Dual-write to database if enabled
            self._dual_write_delete(expense_id)
            
            return True
        
        return False
    
    def bulk_delete_expenses(self, ids: List[int]) -> int:
        """Delete multiple expenses.
        
        Args:
            ids: List of expense IDs to delete
        
        Returns:
            Number of expenses actually deleted
        """
        expenses = self._load_expenses()
        initial_count = len(expenses)
        
        expenses = [e for e in expenses if e["id"] not in ids]
        deleted_count = initial_count - len(expenses)
        
        if deleted_count > 0:
            # Save to JSON (primary storage)
            self._save_expenses(expenses)
            
            # Dual-write to database if enabled
            self._dual_write_bulk_delete(ids)
        
        return deleted_count


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
