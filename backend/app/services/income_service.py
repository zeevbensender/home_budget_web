"""
Income service layer for business logic.

This service handles income-related business logic and data access.
Uses PostgreSQL database as primary storage (Phase 5 - JSON storage removed).
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.settings import get_default_currency
from app.models.income import Income
from app.repositories.income_repository import IncomeRepository

logger = logging.getLogger(__name__)


class IncomeService:
    """Service for managing incomes.
    
    Provides business logic layer between routers and data access.
    Handles data transformation, validation, and storage operations.
    Uses PostgreSQL database as primary storage.
    """
    
    def __init__(self, db: Session):
        """Initialize income service.
        
        Args:
            db: Database session for repository access
        """
        self.db = db
        self.repository = IncomeRepository(db)
    
    def _convert_from_db_format(self, income) -> Dict[str, Any]:
        """Convert SQLAlchemy model instance to dictionary format.
        
        Args:
            income: SQLAlchemy Income model instance
        
        Returns:
            Dictionary with date as string and amount as float
        """
        # Handle both model instances and dictionaries
        if isinstance(income, Income):
            return {
                "id": income.id,
                "date": income.date.strftime("%Y-%m-%d"),
                "category": income.category,
                "amount": float(income.amount),
                "account": income.account,
                "currency": income.currency,
                "notes": income.notes,
            }
        return income
    
    def list_incomes(self) -> List[Dict[str, Any]]:
        """Get all incomes.
        
        Returns:
            List of income dictionaries
        """
        incomes = self.repository.list(order_by="-date")
        return [self._convert_from_db_format(i) for i in incomes]
    
    def get_income(self, income_id: int) -> Optional[Dict[str, Any]]:
        """Get a single income by ID.
        
        Args:
            income_id: The income ID
        
        Returns:
            Income dictionary if found, None otherwise
        """
        income = self.repository.get(income_id)
        return self._convert_from_db_format(income) if income else None
    
    def create_income(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new income.
        
        Args:
            data: Income data dictionary
        
        Returns:
            Created income with assigned ID
        """
        # Auto-fill currency if missing
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        
        # Create in PostgreSQL database
        created = self.repository.create(data)
        return self._convert_from_db_format(created)
    
    def update_income(
        self,
        income_id: int,
        field: str,
        value: Any,
    ) -> Optional[Dict[str, Any]]:
        """Update a single field of an income.
        
        Args:
            income_id: The income ID
            field: The field name to update
            value: The new value
        
        Returns:
            Updated income if found, None otherwise
        """
        # Get existing income from database
        existing = self.repository.get(income_id)
        if not existing:
            return None
        
        # Handle currency special case
        if field == "currency" and value is None:
            value = get_default_currency()
        
        # Update in PostgreSQL database
        update_data = {field: value}
        updated = self.repository.update(income_id, update_data)
        if not updated:
            return None
        
        return self._convert_from_db_format(updated)
    
    def delete_income(self, income_id: int) -> bool:
        """Delete an income.
        
        Args:
            income_id: The income ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        # Check if exists first
        existing = self.repository.get(income_id)
        if not existing:
            return False
        
        # Delete from PostgreSQL database
        return self.repository.delete(income_id)
    
    def bulk_delete_incomes(self, ids: List[int]) -> int:
        """Delete multiple incomes.
        
        Args:
            ids: List of income IDs to delete
        
        Returns:
            Number of incomes actually deleted
        """
        # Delete from PostgreSQL database
        return self.repository.bulk_delete(ids)
