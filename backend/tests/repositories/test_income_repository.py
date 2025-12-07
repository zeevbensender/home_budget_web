"""Tests for IncomeRepository."""

from datetime import date
from decimal import Decimal

import pytest

from app.repositories.income_repository import IncomeRepository


class TestIncomeRepositoryCreate:
    """Tests for create operation."""
    
    def test_create_income(self, db_session):
        """Test creating a new income."""
        repo = IncomeRepository(db_session)
        
        income_data = {
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("8200.00"),
            "account": "Bank Leumi",
            "currency": "₪",
            "notes": "November salary",
        }
        
        income = repo.create(income_data)
        
        assert income.id is not None
        assert income.date == date(2025, 11, 1)
        assert income.category == "Salary"
        assert income.amount == Decimal("8200.00")
        assert income.account == "Bank Leumi"
        assert income.currency == "₪"
        assert income.notes == "November salary"
    
    def test_create_income_minimal(self, db_session):
        """Test creating income with minimal required fields."""
        repo = IncomeRepository(db_session)
        
        income_data = {
            "date": date(2025, 11, 10),
            "category": "Freelance",
            "amount": Decimal("1250.00"),
            "account": "PayPal",
            "currency": "₪",
        }
        
        income = repo.create(income_data)
        
        assert income.id is not None
        assert income.date == date(2025, 11, 10)
        assert income.category == "Freelance"
        assert income.amount == Decimal("1250.00")
        assert income.notes is None


class TestIncomeRepositoryGet:
    """Tests for get operation."""
    
    def test_get_existing_income(self, db_session):
        """Test getting an existing income by ID."""
        repo = IncomeRepository(db_session)
        
        income_data = {
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        }
        
        created = repo.create(income_data)
        fetched = repo.get(created.id)
        
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.category == "Salary"
    
    def test_get_nonexistent_income(self, db_session):
        """Test getting a non-existent income returns None."""
        repo = IncomeRepository(db_session)
        
        fetched = repo.get(999)
        
        assert fetched is None


class TestIncomeRepositoryList:
    """Tests for list operation."""
    
    def test_list_all_incomes(self, db_session):
        """Test listing all incomes."""
        repo = IncomeRepository(db_session)
        
        # Create multiple incomes
        for i in range(3):
            repo.create({
                "date": date(2025, 11, i + 1),
                "category": f"Category{i}",
                "amount": Decimal("1000.00"),
                "account": "Bank",
                "currency": "₪",
            })
        
        incomes = repo.list()
        
        assert len(incomes) == 3
    
    def test_list_with_filters(self, db_session):
        """Test listing incomes with filters."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Freelance",
            "amount": Decimal("1000.00"),
            "account": "PayPal",
            "currency": "₪",
        })
        
        incomes = repo.list(filters={"category": "Salary"})
        
        assert len(incomes) == 1
        assert incomes[0].category == "Salary"


class TestIncomeRepositoryUpdate:
    """Tests for update operation."""
    
    def test_update_income(self, db_session):
        """Test updating an existing income."""
        repo = IncomeRepository(db_session)
        
        income = repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        
        updated = repo.update(income.id, {
            "amount": Decimal("5500.00"),
            "notes": "Bonus included",
        })
        
        assert updated is not None
        assert updated.id == income.id
        assert updated.amount == Decimal("5500.00")
        assert updated.notes == "Bonus included"
        assert updated.category == "Salary"  # Unchanged
    
    def test_update_nonexistent_income(self, db_session):
        """Test updating a non-existent income returns None."""
        repo = IncomeRepository(db_session)
        
        updated = repo.update(999, {"amount": Decimal("1000.00")})
        
        assert updated is None


class TestIncomeRepositoryDelete:
    """Tests for delete operation."""
    
    def test_delete_income(self, db_session):
        """Test deleting an existing income."""
        repo = IncomeRepository(db_session)
        
        income = repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        
        deleted = repo.delete(income.id)
        
        assert deleted is True
        assert repo.get(income.id) is None
    
    def test_delete_nonexistent_income(self, db_session):
        """Test deleting a non-existent income returns False."""
        repo = IncomeRepository(db_session)
        
        deleted = repo.delete(999)
        
        assert deleted is False


class TestIncomeRepositoryBulkDelete:
    """Tests for bulk_delete operation."""
    
    def test_bulk_delete_incomes(self, db_session):
        """Test bulk deleting multiple incomes."""
        repo = IncomeRepository(db_session)
        
        # Create 3 incomes
        ids = []
        for i in range(3):
            income = repo.create({
                "date": date(2025, 11, i + 1),
                "category": "Category",
                "amount": Decimal("1000.00"),
                "account": "Bank",
                "currency": "₪",
            })
            ids.append(income.id)
        
        # Delete 2 of them
        deleted_count = repo.bulk_delete(ids[:2])
        
        assert deleted_count == 2
        assert repo.count() == 1
    
    def test_bulk_delete_nonexistent_ids(self, db_session):
        """Test bulk deleting with non-existent IDs."""
        repo = IncomeRepository(db_session)
        
        deleted_count = repo.bulk_delete([999, 1000])
        
        assert deleted_count == 0


class TestIncomeRepositoryCount:
    """Tests for count operation."""
    
    def test_count_all_incomes(self, db_session):
        """Test counting all incomes."""
        repo = IncomeRepository(db_session)
        
        # Create 3 incomes
        for i in range(3):
            repo.create({
                "date": date(2025, 11, i + 1),
                "category": "Category",
                "amount": Decimal("1000.00"),
                "account": "Bank",
                "currency": "₪",
            })
        
        count = repo.count()
        
        assert count == 3
    
    def test_count_with_filters(self, db_session):
        """Test counting incomes with filters."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Freelance",
            "amount": Decimal("1000.00"),
            "account": "PayPal",
            "currency": "₪",
        })
        
        count = repo.count(filters={"category": "Salary"})
        
        assert count == 1


class TestIncomeRepositoryExists:
    """Tests for exists operation."""
    
    def test_exists_true(self, db_session):
        """Test exists returns True for existing income."""
        repo = IncomeRepository(db_session)
        
        income = repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        
        exists = repo.exists(income.id)
        
        assert exists is True
    
    def test_exists_false(self, db_session):
        """Test exists returns False for non-existent income."""
        repo = IncomeRepository(db_session)
        
        exists = repo.exists(999)
        
        assert exists is False


class TestIncomeRepositoryCustomMethods:
    """Tests for custom repository methods."""
    
    def test_get_by_date_range(self, db_session):
        """Test getting incomes by date range."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with different dates
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 15),
            "category": "Freelance",
            "amount": Decimal("1000.00"),
            "account": "PayPal",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 12, 1),
            "category": "Bonus",
            "amount": Decimal("2000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        
        incomes = repo.get_by_date_range(date(2025, 11, 1), date(2025, 11, 30))
        
        assert len(incomes) == 2
    
    def test_get_by_category(self, db_session):
        """Test getting incomes by category."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Salary",
            "amount": Decimal("1000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 3),
            "category": "Freelance",
            "amount": Decimal("750.00"),
            "account": "PayPal",
            "currency": "₪",
        })
        
        incomes = repo.get_by_category("Salary")
        
        assert len(incomes) == 2
    
    def test_get_total_by_category(self, db_session):
        """Test calculating total by category."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with same category
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Salary",
            "amount": Decimal("500.50"),
            "account": "Bank",
            "currency": "₪",
        })
        
        total = repo.get_total_by_category("Salary")
        
        assert total == Decimal("5500.50")
    
    def test_get_total_by_date_range(self, db_session):
        """Test calculating total by date range."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with different dates
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 15),
            "category": "Freelance",
            "amount": Decimal("1000.00"),
            "account": "PayPal",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 12, 1),
            "category": "Bonus",
            "amount": Decimal("2000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        
        total = repo.get_total_by_date_range(date(2025, 11, 1), date(2025, 11, 30))
        
        assert total == Decimal("6000.00")
    
    def test_get_categories(self, db_session):
        """Test getting unique categories."""
        repo = IncomeRepository(db_session)
        
        # Create incomes with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Salary",
            "amount": Decimal("5000.00"),
            "account": "Bank",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Freelance",
            "amount": Decimal("1000.00"),
            "account": "PayPal",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 3),
            "category": "Salary",
            "amount": Decimal("500.00"),
            "account": "Bank",
            "currency": "₪",
        })
        
        categories = repo.get_categories()
        
        assert len(categories) == 2
        assert "Salary" in categories
        assert "Freelance" in categories
