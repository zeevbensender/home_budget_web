"""
Income service layer for business logic.

This service handles income-related business logic and data access.
Phase 2: Uses JSON storage
Phase 3: Adds dual-write to PostgreSQL
Phase 4: Switches to reading from PostgreSQL
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.feature_flags import is_feature_enabled
from app.core.settings import get_default_currency
from app.core.storage import load_json, save_json
from app.repositories.income_repository import IncomeRepository

logger = logging.getLogger(__name__)


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
    
    def _convert_to_db_format(self, income: Dict[str, Any]) -> Dict[str, Any]:
        """Convert income dict to database format.
        
        Args:
            income: Income dictionary
        
        Returns:
            Dictionary formatted for database
        """
        db_data = income.copy()
        
        # Convert date string to date object if needed
        if isinstance(db_data.get("date"), str):
            db_data["date"] = datetime.strptime(db_data["date"], "%Y-%m-%d").date()
        
        # Convert amount to Decimal if needed
        if isinstance(db_data.get("amount"), (int, float)):
            db_data["amount"] = Decimal(str(db_data["amount"]))
        
        return db_data
    
    def _dual_write_create(self, income: Dict[str, Any]) -> None:
        """Write income to database in dual-write mode.
        
        Args:
            income: Income dictionary to write
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            db_data = self._convert_to_db_format(income)
            self.repository.create(db_data)
            logger.info(f"Dual-write: Created income {income['id']} in database")
        except Exception as e:
            logger.warning(f"Dual-write failed for income {income['id']}: {e}")
    
    def _dual_write_update(self, income_id: int, data: Dict[str, Any]) -> None:
        """Update income in database in dual-write mode.
        
        Args:
            income_id: Income ID
            data: Updated fields
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            db_data = self._convert_to_db_format(data)
            self.repository.update(income_id, db_data)
            logger.info(f"Dual-write: Updated income {income_id} in database")
        except Exception as e:
            logger.warning(f"Dual-write failed for income {income_id}: {e}")
    
    def _dual_write_delete(self, income_id: int) -> None:
        """Delete income from database in dual-write mode.
        
        Args:
            income_id: Income ID to delete
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            self.repository.delete(income_id)
            logger.info(f"Dual-write: Deleted income {income_id} from database")
        except Exception as e:
            logger.warning(f"Dual-write failed for income {income_id}: {e}")
    
    def _dual_write_bulk_delete(self, ids: List[int]) -> None:
        """Bulk delete incomes from database in dual-write mode.
        
        Args:
            ids: List of income IDs to delete
        """
        if not is_feature_enabled("DUAL_WRITE_ENABLED"):
            return
        
        if not self.repository:
            logger.warning("Dual-write enabled but no database session available")
            return
        
        try:
            deleted = self.repository.bulk_delete(ids)
            logger.info(f"Dual-write: Bulk deleted {deleted} incomes from database")
        except Exception as e:
            logger.warning(f"Dual-write bulk delete failed: {e}")
    
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
        
        # Save to JSON (primary storage)
        self._save_incomes(incomes)
        
        # Dual-write to database if enabled
        self._dual_write_create(income)
        
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
                
                # Save to JSON (primary storage)
                self._save_incomes(incomes)
                
                # Dual-write to database if enabled
                self._dual_write_update(income_id, {field: income[field]})
                
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
            # Save to JSON (primary storage)
            self._save_incomes(incomes)
            
            # Dual-write to database if enabled
            self._dual_write_delete(income_id)
            
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
            # Save to JSON (primary storage)
            self._save_incomes(incomes)
            
            # Dual-write to database if enabled
            self._dual_write_bulk_delete(ids)
        
        return deleted_count
