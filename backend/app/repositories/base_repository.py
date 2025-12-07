"""Base repository class providing common CRUD operations for all repositories."""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.core.database import Base

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Abstract base repository class implementing common CRUD operations.

    This class provides a standard interface for all repositories in the application,
    ensuring consistency in data access patterns and making it easy to swap
    storage backends if needed.

    Type Parameters:
        ModelType: The SQLAlchemy model class this repository manages

    Attributes:
        model_class: The SQLAlchemy model class
        db: The database session

    Example:
        class ExpenseRepository(BaseRepository[Expense]):
            def __init__(self, db: Session):
                super().__init__(Expense, db)
    """

    def __init__(self, model_class: Type[ModelType], db: Session):
        """
        Initialize the repository.

        Args:
            model_class: The SQLAlchemy model class this repository will manage
            db: The database session to use for queries
        """
        self.model_class = model_class
        self.db = db

    def create(self, **kwargs: Any) -> ModelType:
        """
        Create a new record in the database.

        Args:
            **kwargs: Field values for the new record

        Returns:
            The created model instance with populated ID and defaults

        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.model_class(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get(self, record_id: int) -> Optional[ModelType]:
        """
        Retrieve a single record by ID.

        Args:
            record_id: The primary key ID of the record

        Returns:
            The model instance if found, None otherwise
        """
        return self.db.query(self.model_class).filter(
            self.model_class.id == record_id
        ).first()

    def list(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        **filters: Any
    ) -> List[ModelType]:
        """
        List records with optional filtering and pagination.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return (None for all)
            **filters: Field-value pairs to filter by (exact match)

        Returns:
            List of model instances matching the filters
        """
        query = self.db.query(self.model_class)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)

        # Apply pagination
        query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def update(self, record_id: int, **kwargs: Any) -> Optional[ModelType]:
        """
        Update an existing record.

        Args:
            record_id: The primary key ID of the record to update
            **kwargs: Field-value pairs to update

        Returns:
            The updated model instance if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.get(record_id)
        if instance is None:
            return None

        for field, value in kwargs.items():
            if hasattr(instance, field):
                setattr(instance, field, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, record_id: int) -> bool:
        """
        Delete a record by ID.

        Args:
            record_id: The primary key ID of the record to delete

        Returns:
            True if record was deleted, False if record was not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        instance = self.get(record_id)
        if instance is None:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True

    def bulk_delete(self, record_ids: List[int]) -> int:
        """
        Delete multiple records by their IDs.

        Args:
            record_ids: List of primary key IDs to delete

        Returns:
            Number of records actually deleted

        Raises:
            SQLAlchemyError: If database operation fails
        """
        deleted_count = self.db.query(self.model_class).filter(
            self.model_class.id.in_(record_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted_count

    def count(self, **filters: Any) -> int:
        """
        Count records matching the given filters.

        Args:
            **filters: Field-value pairs to filter by (exact match)

        Returns:
            Number of records matching the filters
        """
        query = self.db.query(self.model_class)

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model_class, field):
                query = query.filter(getattr(self.model_class, field) == value)

        return query.count()

    def exists(self, record_id: int) -> bool:
        """
        Check if a record exists by ID.

        Args:
            record_id: The primary key ID to check

        Returns:
            True if record exists, False otherwise
        """
        return self.db.query(self.model_class).filter(
            self.model_class.id == record_id
        ).count() > 0
