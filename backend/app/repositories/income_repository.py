"""Income repository for managing income data access."""

from datetime import date
from decimal import Decimal
from typing import List, Optional, Type

from sqlalchemy.orm import Session

from app.models.income import Income
from app.repositories.base_repository import BaseRepository


class IncomeRepository(BaseRepository[Income]):
    """Repository for Income model data access.
    
    Provides CRUD operations and custom query methods for incomes.
    Inherits common operations from BaseRepository.
    """
    
    @property
    def model(self) -> Type[Income]:
        """Return the Income model class.
        
        Returns:
            Income model class
        """
        return Income
    
    def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[Income]:
        """Get incomes within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of incomes in the date range
        """
        query = self.db.query(self.model).filter(
            self.model.date >= start_date,
            self.model.date <= end_date,
        ).order_by(self.model.date.desc())
        
        query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[Income]:
        """Get incomes by category.
        
        Args:
            category: Category name to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of incomes from the category
        """
        query = self.db.query(self.model).filter(
            self.model.category == category
        ).order_by(self.model.date.desc())
        
        query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_total_by_category(self, category: str) -> Decimal:
        """Calculate total amount for a category.
        
        Args:
            category: Category name
        
        Returns:
            Sum of income amounts from the category
        """
        from sqlalchemy import func
        
        result = self.db.query(func.sum(self.model.amount)).filter(
            self.model.category == category
        ).scalar()
        
        return result or Decimal(0)
    
    def get_total_by_date_range(
        self,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """Calculate total amount for a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        
        Returns:
            Sum of income amounts in the date range
        """
        from sqlalchemy import func
        
        result = self.db.query(func.sum(self.model.amount)).filter(
            self.model.date >= start_date,
            self.model.date <= end_date,
        ).scalar()
        
        return result or Decimal(0)
    
    def get_categories(self) -> List[str]:
        """Get list of unique categories.
        
        Returns:
            List of unique category names
        """
        result = self.db.query(self.model.category).distinct().order_by(
            self.model.category
        ).all()
        
        return [row[0] for row in result]
