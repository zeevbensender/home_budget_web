"""Base repository abstract class for data access layer.

This module provides the abstract base class for all repository implementations.
Repositories encapsulate data access logic and provide a clean interface for
CRUD operations on database models.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Base

# Type variable for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Abstract base repository for data access operations.
    
    This class provides common CRUD operations that can be used by all
    repository implementations. Subclasses must specify their model type
    and can override methods to add custom behavior.
    
    Type Parameters:
        ModelType: The SQLAlchemy model class this repository manages
    
    Attributes:
        model: The SQLAlchemy model class
        db: The database session
    """
    
    def __init__(self, db: Session):
        """Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    @property
    @abstractmethod
    def model(self) -> Type[ModelType]:
        """Return the SQLAlchemy model class for this repository.
        
        Returns:
            The model class (e.g., Expense, Income)
        """
        pass
    
    def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record in the database.
        
        Args:
            data: Dictionary of field values for the new record
        
        Returns:
            The created model instance with database-assigned ID
        
        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def get(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID.
        
        Args:
            id: Primary key value
        
        Returns:
            Model instance if found, None otherwise
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """List records with optional filtering and pagination.
        
        Args:
            filters: Dictionary of field:value pairs to filter by
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            order_by: Field name to order by (prefix with '-' for descending)
        
        Returns:
            List of model instances matching criteria
        """
        query = self.db.query(self.model)
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        # Apply ordering
        if order_by:
            if order_by.startswith('-'):
                field = order_by[1:]
                if hasattr(self.model, field):
                    query = query.order_by(getattr(self.model, field).desc())
            else:
                if hasattr(self.model, order_by):
                    query = query.order_by(getattr(self.model, order_by))
        
        # Apply pagination
        query = query.offset(skip)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """Update an existing record.
        
        Args:
            id: Primary key of record to update
            data: Dictionary of fields to update
        
        Returns:
            Updated model instance if found, None otherwise
        
        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.get(id)
        if instance is None:
            return None
        
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete a single record by ID.
        
        Args:
            id: Primary key of record to delete
        
        Returns:
            True if record was deleted, False if not found
        
        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.get(id)
        if instance is None:
            return False
        
        self.db.delete(instance)
        self.db.commit()
        return True
    
    def bulk_delete(self, ids: List[int]) -> int:
        """Delete multiple records by their IDs.
        
        Args:
            ids: List of primary keys to delete
        
        Returns:
            Number of records actually deleted
        
        Raises:
            SQLAlchemyError: If database operation fails
        """
        deleted = self.db.query(self.model).filter(self.model.id.in_(ids)).delete(
            synchronize_session=False
        )
        self.db.commit()
        return deleted
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching optional filters.
        
        Args:
            filters: Dictionary of field:value pairs to filter by
        
        Returns:
            Number of records matching criteria
        """
        query = self.db.query(func.count(self.model.id))
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        return query.scalar()
    
    def exists(self, id: int) -> bool:
        """Check if a record exists by ID.
        
        Args:
            id: Primary key to check
        
        Returns:
            True if record exists, False otherwise
        """
        return self.db.query(self.model.id).filter(self.model.id == id).first() is not None
