"""
Income service layer for business logic.

This service handles income-related business logic and data access.
Phase 2: Uses JSON storage
Phase 3: Adds dual-write to PostgreSQL
Phase 4: Switches to reading from PostgreSQL
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.settings import get_default_currency
from app.core.storage import load_json, save_json
from app.repositories.income_repository import IncomeRepository


class IncomeService:
    """Service for managing incomes.
    
    Provides business logic layer between routers and data access.
    Handles data transformation, validation, and storage operations.
    """
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize income service.
        
        Args:
            db: Optional database session (for dual-write and repository access)
        """
        self.db = db
        self.repository = IncomeRepository(db) if db else None
        self._incomes_cache: Optional[List[Dict[str, Any]]] = None
    
    def _load_incomes(self) -> List[Dict[str, Any]]:
        """Load incomes from JSON storage.
        
        Returns:
            List of income dictionaries
        """
        return load_json("incomes.json", [])
    
    def _save_incomes(self, incomes: List[Dict[str, Any]]) -> None:
        """Save incomes to JSON storage.
        
        Args:
            incomes: List of income dictionaries to save
        """
        save_json("incomes.json", incomes)
    
    def list_incomes(self) -> List[Dict[str, Any]]:
        """Get all incomes.
        
        Returns:
            List of income dictionaries
        """
        return self._load_incomes()
    
    def get_income(self, income_id: int) -> Optional[Dict[str, Any]]:
        """Get a single income by ID.
        
        Args:
            income_id: The income ID
        
        Returns:
            Income dictionary if found, None otherwise
        """
        incomes = self._load_incomes()
        for income in incomes:
            if income.get("id") == income_id:
                return income
        return None
    
    def create_income(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new income.
        
        Args:
            data: Income data dictionary
        
        Returns:
            Created income with assigned ID
        """
        incomes = self._load_incomes()
        
        # Generate new ID
        new_id = max([i["id"] for i in incomes], default=0) + 1
        
        # Auto-fill currency if missing
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        
        # Create income record
        income = {**data, "id": new_id}
        incomes.append(income)
        
        # Save to JSON
        self._save_incomes(incomes)
        
        return income
    
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
        incomes = self._load_incomes()
        
        for income in incomes:
            if income["id"] == income_id:
                # Validate field exists
                if field not in income:
                    raise ValueError(f"Invalid field: {field}")
                
                # Handle currency special case
                if field == "currency" and value is None:
                    income["currency"] = get_default_currency()
                else:
                    income[field] = value
                
                self._save_incomes(incomes)
                return income
        
        return None
    
    def delete_income(self, income_id: int) -> bool:
        """Delete an income.
        
        Args:
            income_id: The income ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        incomes = self._load_incomes()
        initial_count = len(incomes)
        
        incomes = [i for i in incomes if i["id"] != income_id]
        
        if len(incomes) < initial_count:
            self._save_incomes(incomes)
            return True
        
        return False
    
    def bulk_delete_incomes(self, ids: List[int]) -> int:
        """Delete multiple incomes.
        
        Args:
            ids: List of income IDs to delete
        
        Returns:
            Number of incomes actually deleted
        """
        incomes = self._load_incomes()
        initial_count = len(incomes)
        
        incomes = [i for i in incomes if i["id"] not in ids]
        deleted_count = initial_count - len(incomes)
        
        if deleted_count > 0:
            self._save_incomes(incomes)
        
        return deleted_count
