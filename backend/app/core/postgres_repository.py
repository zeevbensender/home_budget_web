"""PostgreSQL repository implementation.

This module provides a concrete implementation of the Repository interface
that stores data in PostgreSQL using SQLAlchemy.
"""

from datetime import date
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_session_factory
from app.core.models import Expense, Income
from app.core.repository import Repository


class PostgresRepository(Repository):
    """Repository implementation using PostgreSQL with SQLAlchemy."""

    # Map entity types to model classes
    _model_map = {
        "expenses": Expense,
        "incomes": Income,
    }

    def __init__(self, session: Session | None = None) -> None:
        """Initialize the PostgreSQL repository.

        Args:
            session: Optional SQLAlchemy session. If not provided,
                    a new session will be created for each operation.
        """
        self._session = session

    def _get_session(self) -> Session:
        """Get a session for database operations."""
        if self._session is not None:
            return self._session
        # Create a new session if none provided
        session_factory = get_session_factory()
        return session_factory()

    def _get_model(self, entity_type: str):
        """Get the model class for an entity type."""
        if entity_type not in self._model_map:
            raise ValueError(f"Unknown entity type: {entity_type}")
        return self._model_map[entity_type]

    def _close_session(self, session: Session) -> None:
        """Close session if it was created internally."""
        if self._session is None:
            session.close()

    @staticmethod
    def _parse_date(date_str: str) -> date:
        """Parse a date string in ISO format."""
        return date.fromisoformat(date_str)

    def list_all(self, entity_type: str) -> list[dict[str, Any]]:
        """Retrieve all items of a given entity type."""
        model = self._get_model(entity_type)
        session = self._get_session()
        try:
            items = session.query(model).all()
            return [item.to_dict() for item in items]
        finally:
            self._close_session(session)

    def get_by_id(self, entity_type: str, entity_id: int) -> dict[str, Any] | None:
        """Retrieve a single item by ID."""
        model = self._get_model(entity_type)
        session = self._get_session()
        try:
            item = session.get(model, entity_id)
            return item.to_dict() if item else None
        finally:
            self._close_session(session)

    def create(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new entity."""
        model = self._get_model(entity_type)
        session = self._get_session()
        try:
            # Convert date string to date object if present
            if "date" in data and isinstance(data["date"], str):
                data = {**data, "date": self._parse_date(data["date"])}

            # Remove id if present (let DB generate it)
            create_data = {k: v for k, v in data.items() if k != "id"}

            item = model(**create_data)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item.to_dict()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            self._close_session(session)

    def update(
        self, entity_type: str, entity_id: int, field: str, value: Any
    ) -> dict[str, Any] | None:
        """Update a field on an existing entity."""
        model = self._get_model(entity_type)
        session = self._get_session()
        try:
            item = session.get(model, entity_id)
            if item is None:
                return None

            # Convert date string to date object if updating date field
            if field == "date" and isinstance(value, str):
                value = self._parse_date(value)

            setattr(item, field, value)
            session.commit()
            session.refresh(item)
            return item.to_dict()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            self._close_session(session)

    def delete(self, entity_type: str, entity_id: int) -> bool:
        """Delete an entity by ID."""
        model = self._get_model(entity_type)
        session = self._get_session()
        try:
            item = session.get(model, entity_id)
            if item is None:
                return False

            session.delete(item)
            session.commit()
            return True
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            self._close_session(session)

    def bulk_delete(self, entity_type: str, ids: list[int]) -> int:
        """Delete multiple entities by IDs."""
        model = self._get_model(entity_type)
        session = self._get_session()
        try:
            deleted = (
                session.query(model)
                .filter(model.id.in_(ids))
                .delete(synchronize_session=False)
            )
            session.commit()
            return deleted
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            self._close_session(session)


# Singleton instance for use across the application
_postgres_repository: PostgresRepository | None = None


def get_postgres_repository() -> PostgresRepository:
    """Get the singleton PostgreSQL repository instance."""
    global _postgres_repository
    if _postgres_repository is None:
        _postgres_repository = PostgresRepository()
    return _postgres_repository
