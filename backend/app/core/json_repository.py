"""JSON file-based repository implementation.

This module provides a concrete implementation of the Repository interface
that stores data in JSON files.
"""

from typing import Any

from app.core.repository import Repository
from app.core.storage import load_json, save_json


class JsonRepository(Repository):
    """Repository implementation using JSON file storage."""

    # Default data for each entity type
    DEFAULT_EXPENSES = [
        {
            "id": 1,
            "date": "2025-11-01",
            "business": "SuperSal",
            "category": "Groceries",
            "amount": 142.50,
            "account": "Visa 1234",
            "currency": "₪",
            "notes": "Weekly shopping",
        },
        {
            "id": 2,
            "date": "2025-11-05",
            "business": "Rav-Kav",
            "category": "Transport",
            "amount": 15.00,
            "account": "Cash",
            "currency": "₪",
            "notes": "Bus to work",
        },
    ]

    DEFAULT_INCOMES = [
        {
            "id": 1,
            "date": "2025-11-01",
            "category": "Salary",
            "amount": 8200.00,
            "account": "Bank Leumi",
            "currency": "₪",
            "notes": "November salary",
        },
        {
            "id": 2,
            "date": "2025-11-10",
            "category": "Freelance",
            "amount": 1250.00,
            "account": "PayPal",
            "currency": "₪",
            "notes": "Client project",
        },
    ]

    def __init__(self) -> None:
        """Initialize the JSON repository with cached data."""
        self._cache: dict[str, list[dict[str, Any]]] = {}

    def clear_cache(self) -> None:
        """Clear the in-memory cache, forcing data to be reloaded from files."""
        self._cache = {}

    def _get_filename(self, entity_type: str) -> str:
        """Get the JSON filename for an entity type."""
        return f"{entity_type}.json"

    def _get_default(self, entity_type: str) -> list[dict[str, Any]]:
        """Get the default data for an entity type."""
        if entity_type == "expenses":
            return self.DEFAULT_EXPENSES.copy()
        elif entity_type == "incomes":
            return self.DEFAULT_INCOMES.copy()
        return []

    def _load(self, entity_type: str) -> list[dict[str, Any]]:
        """Load data for an entity type, using cache if available."""
        if entity_type not in self._cache:
            filename = self._get_filename(entity_type)
            default = self._get_default(entity_type)
            self._cache[entity_type] = load_json(filename, default)
        return self._cache[entity_type]

    def _save(self, entity_type: str) -> None:
        """Save data for an entity type."""
        filename = self._get_filename(entity_type)
        save_json(filename, self._cache[entity_type])

    def list_all(self, entity_type: str) -> list[dict[str, Any]]:
        """Retrieve all items of a given entity type."""
        return self._load(entity_type)

    def get_by_id(self, entity_type: str, entity_id: int) -> dict[str, Any] | None:
        """Retrieve a single item by ID."""
        items = self._load(entity_type)
        for item in items:
            if item["id"] == entity_id:
                return item
        return None

    def create(self, entity_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new entity."""
        items = self._load(entity_type)
        new_id = max([item["id"] for item in items], default=0) + 1
        new_item = {**data, "id": new_id}
        items.append(new_item)
        self._save(entity_type)
        return new_item

    def update(
        self, entity_type: str, entity_id: int, field: str, value: Any
    ) -> dict[str, Any] | None:
        """Update a field on an existing entity."""
        items = self._load(entity_type)
        for item in items:
            if item["id"] == entity_id:
                item[field] = value
                self._save(entity_type)
                return item
        return None

    def delete(self, entity_type: str, entity_id: int) -> bool:
        """Delete an entity by ID."""
        items = self._load(entity_type)
        original_len = len(items)
        self._cache[entity_type] = [item for item in items if item["id"] != entity_id]
        if len(self._cache[entity_type]) < original_len:
            self._save(entity_type)
            return True
        return False

    def bulk_delete(self, entity_type: str, ids: list[int]) -> int:
        """Delete multiple entities by IDs."""
        items = self._load(entity_type)
        before = len(items)
        self._cache[entity_type] = [item for item in items if item["id"] not in ids]
        self._save(entity_type)
        return before - len(self._cache[entity_type])


# Singleton instance for use across the application
_json_repository: JsonRepository | None = None


def get_json_repository() -> JsonRepository:
    """Get the singleton JSON repository instance."""
    global _json_repository
    if _json_repository is None:
        _json_repository = JsonRepository()
    return _json_repository
