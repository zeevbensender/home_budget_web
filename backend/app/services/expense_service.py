"""
Expense service layer for business logic.

This service handles expense-related business logic and data access.
Phase 2: Uses JSON storage
Phase 3: Adds dual-write to PostgreSQL
Phase 4: Switches to reading from PostgreSQL
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.feature_flags import is_feature_enabled
from app.core.settings import get_default_currency
from app.core.storage import load_json, save_json
from app.repositories.expense_repository import ExpenseRepository


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
        
        # Save to JSON
        self._save_expenses(expenses)
        
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
                
                self._save_expenses(expenses)
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
            self._save_expenses(expenses)
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
            self._save_expenses(expenses)
        
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
