"""Integration tests for PostgresRepository.

These tests require a running PostgreSQL instance.
Use docker-compose -f docker-compose-postgres.yaml up -d to start one.
"""

import os
from datetime import date

import pytest

# Set test database URL before importing repository modules
os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "postgresql://budget:budget@localhost:5432/budget_db"
)

from app.core.database import create_tables, drop_tables, reset_engine
from app.core.postgres_repository import PostgresRepository


@pytest.fixture(scope="module")
def setup_database():
    """Set up and tear down database tables for tests."""
    reset_engine()
    create_tables()
    yield
    drop_tables()
    reset_engine()


@pytest.fixture
def repository(setup_database):
    """Get a fresh repository instance for each test."""
    repo = PostgresRepository()
    # Clear existing data before each test
    repo.bulk_delete("expenses", [e["id"] for e in repo.list_all("expenses")])
    repo.bulk_delete("incomes", [i["id"] for i in repo.list_all("incomes")])
    return repo


class TestExpensesCRUD:
    """Test CRUD operations for expenses."""

    def test_create_expense(self, repository):
        """Test creating a new expense."""
        data = {
            "date": "2025-11-01",
            "business": "SuperSal",
            "category": "Groceries",
            "amount": 142.50,
            "account": "Visa 1234",
            "currency": "₪",
            "notes": "Weekly shopping",
        }

        result = repository.create("expenses", data)

        assert result["id"] is not None
        assert result["date"] == "2025-11-01"
        assert result["business"] == "SuperSal"
        assert result["category"] == "Groceries"
        assert result["amount"] == 142.50
        assert result["account"] == "Visa 1234"
        assert result["currency"] == "₪"
        assert result["notes"] == "Weekly shopping"

    def test_read_expense_by_id(self, repository):
        """Test reading an expense by ID."""
        data = {
            "date": "2025-11-02",
            "business": "Test Business",
            "category": "Test",
            "amount": 50.00,
            "account": "Cash",
            "currency": "₪",
        }
        created = repository.create("expenses", data)

        result = repository.get_by_id("expenses", created["id"])

        assert result is not None
        assert result["id"] == created["id"]
        assert result["business"] == "Test Business"

    def test_read_nonexistent_expense(self, repository):
        """Test reading a non-existent expense returns None."""
        result = repository.get_by_id("expenses", 99999)
        assert result is None

    def test_list_all_expenses(self, repository):
        """Test listing all expenses."""
        # Create multiple expenses
        repository.create(
            "expenses",
            {
                "date": "2025-11-01",
                "category": "Food",
                "amount": 100.00,
                "account": "Cash",
                "currency": "₪",
            },
        )
        repository.create(
            "expenses",
            {
                "date": "2025-11-02",
                "category": "Transport",
                "amount": 50.00,
                "account": "Card",
                "currency": "₪",
            },
        )

        results = repository.list_all("expenses")

        assert len(results) == 2

    def test_update_expense(self, repository):
        """Test updating an expense field."""
        created = repository.create(
            "expenses",
            {
                "date": "2025-11-01",
                "category": "Original",
                "amount": 100.00,
                "account": "Cash",
                "currency": "₪",
            },
        )

        result = repository.update("expenses", created["id"], "category", "Updated")

        assert result is not None
        assert result["category"] == "Updated"
        assert result["amount"] == 100.00  # Other fields unchanged

    def test_update_nonexistent_expense(self, repository):
        """Test updating a non-existent expense returns None."""
        result = repository.update("expenses", 99999, "category", "Test")
        assert result is None

    def test_delete_expense(self, repository):
        """Test deleting an expense."""
        created = repository.create(
            "expenses",
            {
                "date": "2025-11-01",
                "category": "ToDelete",
                "amount": 100.00,
                "account": "Cash",
                "currency": "₪",
            },
        )

        result = repository.delete("expenses", created["id"])

        assert result is True
        assert repository.get_by_id("expenses", created["id"]) is None

    def test_delete_nonexistent_expense(self, repository):
        """Test deleting a non-existent expense returns False."""
        result = repository.delete("expenses", 99999)
        assert result is False

    def test_bulk_delete_expenses(self, repository):
        """Test bulk deleting multiple expenses."""
        expense1 = repository.create(
            "expenses",
            {
                "date": "2025-11-01",
                "category": "Bulk1",
                "amount": 100.00,
                "account": "Cash",
                "currency": "₪",
            },
        )
        expense2 = repository.create(
            "expenses",
            {
                "date": "2025-11-02",
                "category": "Bulk2",
                "amount": 200.00,
                "account": "Cash",
                "currency": "₪",
            },
        )
        expense3 = repository.create(
            "expenses",
            {
                "date": "2025-11-03",
                "category": "Bulk3",
                "amount": 300.00,
                "account": "Cash",
                "currency": "₪",
            },
        )

        # Delete first two
        deleted = repository.bulk_delete("expenses", [expense1["id"], expense2["id"]])

        assert deleted == 2
        assert repository.get_by_id("expenses", expense1["id"]) is None
        assert repository.get_by_id("expenses", expense2["id"]) is None
        assert repository.get_by_id("expenses", expense3["id"]) is not None


class TestIncomesCRUD:
    """Test CRUD operations for incomes."""

    def test_create_income(self, repository):
        """Test creating a new income."""
        data = {
            "date": "2025-11-01",
            "category": "Salary",
            "amount": 8200.00,
            "account": "Bank Leumi",
            "currency": "₪",
            "notes": "November salary",
        }

        result = repository.create("incomes", data)

        assert result["id"] is not None
        assert result["date"] == "2025-11-01"
        assert result["category"] == "Salary"
        assert result["amount"] == 8200.00
        assert result["account"] == "Bank Leumi"
        assert result["currency"] == "₪"
        assert result["notes"] == "November salary"

    def test_read_income_by_id(self, repository):
        """Test reading an income by ID."""
        data = {
            "date": "2025-11-02",
            "category": "Test Income",
            "amount": 1000.00,
            "account": "Cash",
            "currency": "₪",
        }
        created = repository.create("incomes", data)

        result = repository.get_by_id("incomes", created["id"])

        assert result is not None
        assert result["id"] == created["id"]
        assert result["category"] == "Test Income"

    def test_read_nonexistent_income(self, repository):
        """Test reading a non-existent income returns None."""
        result = repository.get_by_id("incomes", 99999)
        assert result is None

    def test_list_all_incomes(self, repository):
        """Test listing all incomes."""
        repository.create(
            "incomes",
            {
                "date": "2025-11-01",
                "category": "Salary",
                "amount": 5000.00,
                "account": "Bank",
                "currency": "₪",
            },
        )
        repository.create(
            "incomes",
            {
                "date": "2025-11-15",
                "category": "Freelance",
                "amount": 1000.00,
                "account": "PayPal",
                "currency": "₪",
            },
        )

        results = repository.list_all("incomes")

        assert len(results) == 2

    def test_update_income(self, repository):
        """Test updating an income field."""
        created = repository.create(
            "incomes",
            {
                "date": "2025-11-01",
                "category": "Original",
                "amount": 5000.00,
                "account": "Bank",
                "currency": "₪",
            },
        )

        result = repository.update("incomes", created["id"], "category", "Updated")

        assert result is not None
        assert result["category"] == "Updated"
        assert result["amount"] == 5000.00  # Other fields unchanged

    def test_update_nonexistent_income(self, repository):
        """Test updating a non-existent income returns None."""
        result = repository.update("incomes", 99999, "category", "Test")
        assert result is None

    def test_delete_income(self, repository):
        """Test deleting an income."""
        created = repository.create(
            "incomes",
            {
                "date": "2025-11-01",
                "category": "ToDelete",
                "amount": 1000.00,
                "account": "Cash",
                "currency": "₪",
            },
        )

        result = repository.delete("incomes", created["id"])

        assert result is True
        assert repository.get_by_id("incomes", created["id"]) is None

    def test_delete_nonexistent_income(self, repository):
        """Test deleting a non-existent income returns False."""
        result = repository.delete("incomes", 99999)
        assert result is False

    def test_bulk_delete_incomes(self, repository):
        """Test bulk deleting multiple incomes."""
        income1 = repository.create(
            "incomes",
            {
                "date": "2025-11-01",
                "category": "Bulk1",
                "amount": 1000.00,
                "account": "Bank",
                "currency": "₪",
            },
        )
        income2 = repository.create(
            "incomes",
            {
                "date": "2025-11-02",
                "category": "Bulk2",
                "amount": 2000.00,
                "account": "Bank",
                "currency": "₪",
            },
        )
        income3 = repository.create(
            "incomes",
            {
                "date": "2025-11-03",
                "category": "Bulk3",
                "amount": 3000.00,
                "account": "Bank",
                "currency": "₪",
            },
        )

        # Delete first two
        deleted = repository.bulk_delete("incomes", [income1["id"], income2["id"]])

        assert deleted == 2
        assert repository.get_by_id("incomes", income1["id"]) is None
        assert repository.get_by_id("incomes", income2["id"]) is None
        assert repository.get_by_id("incomes", income3["id"]) is not None
