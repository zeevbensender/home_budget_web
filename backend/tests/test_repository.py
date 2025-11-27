"""Unit tests for the repository interface using JSON implementation."""

import pytest
from app.core.json_repository import JsonRepository
from app.core.repository import Repository


@pytest.fixture
def repository() -> JsonRepository:
    """Create a fresh JsonRepository for testing."""
    repo = JsonRepository()
    # Clear the cache to start fresh
    repo._cache = {}
    return repo


def test_repository_inherits_from_abc():
    """Verify JsonRepository is an instance of Repository ABC."""
    repo = JsonRepository()
    assert isinstance(repo, Repository)


def test_list_all_expenses(repository: JsonRepository):
    """Test listing all expenses."""
    expenses = repository.list_all("expenses")
    assert isinstance(expenses, list)
    # Should have the items from the JSON file (or defaults)
    assert len(expenses) > 0
    # Each item should have an id
    for expense in expenses:
        assert "id" in expense


def test_list_all_incomes(repository: JsonRepository):
    """Test listing all incomes."""
    incomes = repository.list_all("incomes")
    assert isinstance(incomes, list)
    assert len(incomes) > 0
    for income in incomes:
        assert "id" in income


def test_get_by_id_existing(repository: JsonRepository):
    """Test getting an existing item by ID."""
    # First get the list to know what IDs exist
    expenses = repository.list_all("expenses")
    if len(expenses) > 0:
        first_id = expenses[0]["id"]
        result = repository.get_by_id("expenses", first_id)
        assert result is not None
        assert result["id"] == first_id


def test_get_by_id_not_found(repository: JsonRepository):
    """Test getting a non-existing item by ID."""
    result = repository.get_by_id("expenses", 999999)
    assert result is None


def test_create_expense(repository: JsonRepository):
    """Test creating a new expense."""
    data = {
        "date": "2025-12-01",
        "business": "Test Store",
        "category": "Testing",
        "amount": 100.0,
        "account": "Test Account",
        "currency": "₪",
        "notes": "Test expense",
    }

    created = repository.create("expenses", data)

    assert created is not None
    assert "id" in created
    assert isinstance(created["id"], int)
    assert created["date"] == "2025-12-01"
    assert created["business"] == "Test Store"
    assert created["amount"] == 100.0


def test_create_income(repository: JsonRepository):
    """Test creating a new income."""
    data = {
        "date": "2025-12-01",
        "category": "Bonus",
        "amount": 5000.0,
        "account": "Bank",
        "currency": "₪",
        "notes": "Test income",
    }

    created = repository.create("incomes", data)

    assert created is not None
    assert "id" in created
    assert isinstance(created["id"], int)
    assert created["date"] == "2025-12-01"
    assert created["amount"] == 5000.0


def test_update_existing(repository: JsonRepository):
    """Test updating an existing entity."""
    # First create an item to update
    data = {
        "date": "2025-12-01",
        "business": "Original",
        "category": "Testing",
        "amount": 50.0,
        "account": "Test",
        "currency": "₪",
        "notes": "",
    }
    created = repository.create("expenses", data)
    entity_id = created["id"]

    # Update the item
    updated = repository.update("expenses", entity_id, "amount", 75.0)

    assert updated is not None
    assert updated["id"] == entity_id
    assert updated["amount"] == 75.0


def test_update_not_found(repository: JsonRepository):
    """Test updating a non-existing entity."""
    result = repository.update("expenses", 999999, "amount", 100.0)
    assert result is None


def test_delete_existing(repository: JsonRepository):
    """Test deleting an existing entity."""
    # First create an item to delete
    data = {
        "date": "2025-12-01",
        "business": "To Delete",
        "category": "Testing",
        "amount": 25.0,
        "account": "Test",
        "currency": "₪",
        "notes": "",
    }
    created = repository.create("expenses", data)
    entity_id = created["id"]

    # Delete the item
    result = repository.delete("expenses", entity_id)

    assert result is True

    # Verify it's gone
    found = repository.get_by_id("expenses", entity_id)
    assert found is None


def test_delete_not_found(repository: JsonRepository):
    """Test deleting a non-existing entity."""
    result = repository.delete("expenses", 999999)
    assert result is False


def test_bulk_delete(repository: JsonRepository):
    """Test bulk deleting multiple entities."""
    # Create items to delete
    ids_to_delete = []
    for i in range(3):
        data = {
            "date": f"2025-12-0{i+1}",
            "business": f"Bulk Delete {i}",
            "category": "Testing",
            "amount": float(i * 10),
            "account": "Test",
            "currency": "₪",
            "notes": "",
        }
        created = repository.create("expenses", data)
        ids_to_delete.append(created["id"])

    # Bulk delete
    deleted_count = repository.bulk_delete("expenses", ids_to_delete)

    assert deleted_count == 3

    # Verify they're gone
    for entity_id in ids_to_delete:
        found = repository.get_by_id("expenses", entity_id)
        assert found is None


def test_bulk_delete_partial(repository: JsonRepository):
    """Test bulk delete with some non-existing IDs."""
    # Create one item
    data = {
        "date": "2025-12-01",
        "business": "Partial Delete",
        "category": "Testing",
        "amount": 10.0,
        "account": "Test",
        "currency": "₪",
        "notes": "",
    }
    created = repository.create("expenses", data)
    real_id = created["id"]

    # Try to delete the real ID plus some fake ones
    deleted_count = repository.bulk_delete("expenses", [real_id, 999998, 999999])

    assert deleted_count == 1
