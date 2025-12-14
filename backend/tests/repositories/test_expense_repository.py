"""Tests for ExpenseRepository."""

from datetime import date
from decimal import Decimal

import pytest

from app.repositories.expense_repository import ExpenseRepository


class TestExpenseRepositoryCreate:
    """Tests for create operation."""
    
    def test_create_expense(self, db_session):
        """Test creating a new expense."""
        repo = ExpenseRepository(db_session)
        
        expense_data = {
            "date": date(2025, 11, 1),
            "business": "SuperSal",
            "category": "Groceries",
            "amount": Decimal("142.50"),
            "account": "Visa 1234",
            "currency": "₪",
            "notes": "Weekly shopping",
        }
        
        expense = repo.create(expense_data)
        
        assert expense.id is not None
        assert expense.date == date(2025, 11, 1)
        assert expense.business == "SuperSal"
        assert expense.category == "Groceries"
        assert expense.amount == Decimal("142.50")
        assert expense.account == "Visa 1234"
        assert expense.currency == "₪"
        assert expense.notes == "Weekly shopping"
    
    def test_create_expense_minimal(self, db_session):
        """Test creating expense with minimal required fields."""
        repo = ExpenseRepository(db_session)
        
        expense_data = {
            "date": date(2025, 11, 2),
            "category": "Transport",
            "amount": Decimal("15.00"),
            "account": "Cash",
            "currency": "₪",
        }
        
        expense = repo.create(expense_data)
        
        assert expense.id is not None
        assert expense.date == date(2025, 11, 2)
        assert expense.category == "Transport"
        assert expense.amount == Decimal("15.00")
        assert expense.business is None
        assert expense.notes is None


class TestExpenseRepositoryGet:
    """Tests for get operation."""
    
    def test_get_existing_expense(self, db_session):
        """Test getting an existing expense by ID."""
        repo = ExpenseRepository(db_session)
        
        expense_data = {
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        }
        
        created = repo.create(expense_data)
        fetched = repo.get(created.id)
        
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.category == "Groceries"
    
    def test_get_nonexistent_expense(self, db_session):
        """Test getting a non-existent expense returns None."""
        repo = ExpenseRepository(db_session)
        
        fetched = repo.get(999)
        
        assert fetched is None


class TestExpenseRepositoryList:
    """Tests for list operation."""
    
    def test_list_all_expenses(self, db_session):
        """Test listing all expenses."""
        repo = ExpenseRepository(db_session)
        
        # Create multiple expenses
        for i in range(3):
            repo.create({
                "date": date(2025, 11, i + 1),
                "category": f"Category{i}",
                "amount": Decimal("100.00"),
                "account": "Cash",
                "currency": "₪",
            })
        
        expenses = repo.list()
        
        assert len(expenses) == 3
    
    def test_list_with_filters(self, db_session):
        """Test listing expenses with filters."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Transport",
            "amount": Decimal("50.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        expenses = repo.list(filters={"category": "Groceries"})
        
        assert len(expenses) == 1
        assert expenses[0].category == "Groceries"
    
    def test_list_with_pagination(self, db_session):
        """Test listing expenses with pagination."""
        repo = ExpenseRepository(db_session)
        
        # Create 5 expenses
        for i in range(5):
            repo.create({
                "date": date(2025, 11, i + 1),
                "category": "Category",
                "amount": Decimal("100.00"),
                "account": "Cash",
                "currency": "₪",
            })
        
        # Get page 2 with 2 items per page
        expenses = repo.list(skip=2, limit=2)
        
        assert len(expenses) == 2


class TestExpenseRepositoryUpdate:
    """Tests for update operation."""
    
    def test_update_expense(self, db_session):
        """Test updating an existing expense."""
        repo = ExpenseRepository(db_session)
        
        expense = repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        updated = repo.update(expense.id, {
            "amount": Decimal("150.00"),
            "notes": "Updated amount",
        })
        
        assert updated is not None
        assert updated.id == expense.id
        assert updated.amount == Decimal("150.00")
        assert updated.notes == "Updated amount"
        assert updated.category == "Groceries"  # Unchanged
    
    def test_update_nonexistent_expense(self, db_session):
        """Test updating a non-existent expense returns None."""
        repo = ExpenseRepository(db_session)
        
        updated = repo.update(999, {"amount": Decimal("100.00")})
        
        assert updated is None


class TestExpenseRepositoryDelete:
    """Tests for delete operation."""
    
    def test_delete_expense(self, db_session):
        """Test deleting an existing expense."""
        repo = ExpenseRepository(db_session)
        
        expense = repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        deleted = repo.delete(expense.id)
        
        assert deleted is True
        assert repo.get(expense.id) is None
    
    def test_delete_nonexistent_expense(self, db_session):
        """Test deleting a non-existent expense returns False."""
        repo = ExpenseRepository(db_session)
        
        deleted = repo.delete(999)
        
        assert deleted is False


class TestExpenseRepositoryBulkDelete:
    """Tests for bulk_delete operation."""
    
    def test_bulk_delete_expenses(self, db_session):
        """Test bulk deleting multiple expenses."""
        repo = ExpenseRepository(db_session)
        
        # Create 3 expenses
        ids = []
        for i in range(3):
            expense = repo.create({
                "date": date(2025, 11, i + 1),
                "category": "Category",
                "amount": Decimal("100.00"),
                "account": "Cash",
                "currency": "₪",
            })
            ids.append(expense.id)
        
        # Delete 2 of them
        deleted_count = repo.bulk_delete(ids[:2])
        
        assert deleted_count == 2
        assert repo.count() == 1
    
    def test_bulk_delete_nonexistent_ids(self, db_session):
        """Test bulk deleting with non-existent IDs."""
        repo = ExpenseRepository(db_session)
        
        deleted_count = repo.bulk_delete([999, 1000])
        
        assert deleted_count == 0


class TestExpenseRepositoryCount:
    """Tests for count operation."""
    
    def test_count_all_expenses(self, db_session):
        """Test counting all expenses."""
        repo = ExpenseRepository(db_session)
        
        # Create 3 expenses
        for i in range(3):
            repo.create({
                "date": date(2025, 11, i + 1),
                "category": "Category",
                "amount": Decimal("100.00"),
                "account": "Cash",
                "currency": "₪",
            })
        
        count = repo.count()
        
        assert count == 3
    
    def test_count_with_filters(self, db_session):
        """Test counting expenses with filters."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Transport",
            "amount": Decimal("50.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        count = repo.count(filters={"category": "Groceries"})
        
        assert count == 1


class TestExpenseRepositoryExists:
    """Tests for exists operation."""
    
    def test_exists_true(self, db_session):
        """Test exists returns True for existing expense."""
        repo = ExpenseRepository(db_session)
        
        expense = repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        exists = repo.exists(expense.id)
        
        assert exists is True
    
    def test_exists_false(self, db_session):
        """Test exists returns False for non-existent expense."""
        repo = ExpenseRepository(db_session)
        
        exists = repo.exists(999)
        
        assert exists is False


class TestExpenseRepositoryCustomMethods:
    """Tests for custom repository methods."""
    
    def test_get_by_date_range(self, db_session):
        """Test getting expenses by date range."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with different dates
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 15),
            "category": "Transport",
            "amount": Decimal("50.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 12, 1),
            "category": "Food",
            "amount": Decimal("75.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        expenses = repo.get_by_date_range(date(2025, 11, 1), date(2025, 11, 30))
        
        assert len(expenses) == 2
    
    def test_get_by_category(self, db_session):
        """Test getting expenses by category."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Groceries",
            "amount": Decimal("50.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 3),
            "category": "Transport",
            "amount": Decimal("75.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        expenses = repo.get_by_category("Groceries")
        
        assert len(expenses) == 2
    
    def test_get_total_by_category(self, db_session):
        """Test calculating total by category."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with same category
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Groceries",
            "amount": Decimal("50.50"),
            "account": "Cash",
            "currency": "₪",
        })
        
        total = repo.get_total_by_category("Groceries")
        
        assert total == Decimal("150.50")
    
    def test_get_total_by_date_range(self, db_session):
        """Test calculating total by date range."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with different dates
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 15),
            "category": "Transport",
            "amount": Decimal("50.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 12, 1),
            "category": "Food",
            "amount": Decimal("75.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        total = repo.get_total_by_date_range(date(2025, 11, 1), date(2025, 11, 30))
        
        assert total == Decimal("150.00")
    
    def test_get_categories(self, db_session):
        """Test getting unique categories."""
        repo = ExpenseRepository(db_session)
        
        # Create expenses with different categories
        repo.create({
            "date": date(2025, 11, 1),
            "category": "Groceries",
            "amount": Decimal("100.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 2),
            "category": "Transport",
            "amount": Decimal("50.00"),
            "account": "Cash",
            "currency": "₪",
        })
        repo.create({
            "date": date(2025, 11, 3),
            "category": "Groceries",
            "amount": Decimal("75.00"),
            "account": "Cash",
            "currency": "₪",
        })
        
        categories = repo.get_categories()
        
        assert len(categories) == 2
        assert "Groceries" in categories
        assert "Transport" in categories
