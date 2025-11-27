"""Repository interface for storage abstraction.

This module provides an abstract base class that defines the interface
for data storage operations. Different backends (JSON, Database, etc.)
can implement this interface to allow swapping storage mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Any


class Repository(ABC):
    """Abstract base class defining the repository interface."""

    @abstractmethod
    def list_all(self, entity_type: str) -> list[dict[str, Any]]:
        """Retrieve all items of a given entity type.

        Args:
            entity_type: The type of entity (e.g., 'expenses', 'incomes')

        Returns:
            A list of dictionaries representing the entities
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_type: str, entity_id: int) -> dict[str, Any] | None:
        """Retrieve a single item by ID.

        Args:
            entity_type: The type of entity (e.g., 'expenses', 'incomes')
            entity_id: The unique identifier of the entity

        Returns:
            The entity dictionary if found, None otherwise
        """
        pass

    @abstractmethod
    def create(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new entity.

        Args:
            entity_type: The type of entity (e.g., 'expenses', 'incomes')
            data: The entity data (without ID)

        Returns:
            The created entity with its assigned ID
        """
        pass

    @abstractmethod
    def update(
        self, entity_type: str, entity_id: int, field: str, value: Any
    ) -> dict[str, Any] | None:
        """Update a field on an existing entity.

        Args:
            entity_type: The type of entity (e.g., 'expenses', 'incomes')
            entity_id: The unique identifier of the entity
            field: The field name to update
            value: The new value for the field

        Returns:
            The updated entity if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, entity_type: str, entity_id: int) -> bool:
        """Delete an entity by ID.

        Args:
            entity_type: The type of entity (e.g., 'expenses', 'incomes')
            entity_id: The unique identifier of the entity

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def bulk_delete(self, entity_type: str, ids: list[int]) -> int:
        """Delete multiple entities by IDs.

        Args:
            entity_type: The type of entity (e.g., 'expenses', 'incomes')
            ids: List of entity IDs to delete

        Returns:
            The number of entities deleted
        """
        pass
