"""Tests for ExpenseRepository."""

from datetime import date
from decimal import Decimal

import pytest

from app.repositories.expense_repository import ExpenseRepository


class TestExpenseRepositoryCreate:
    """Tests for ExpenseRepository.create()"""

    def test_create_minimal_expense(self, db_session):
        """Test creating an expense with minimal required fields."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("142.50"),
            account="Visa",
            currency="₪",
        )

        assert expense.id is not None
        assert expense.date == date(2025, 12, 1)
        assert expense.category == "Groceries"
        assert expense.amount == Decimal("142.50")
        assert expense.account == "Visa"
        assert expense.currency == "₪"
        assert expense.business is None
        assert expense.notes is None

    def test_create_full_expense(self, db_session):
        """Test creating an expense with all fields."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            business="SuperSal",
            category="Groceries",
            amount=Decimal("142.50"),
            account="Visa 1234",
            currency="₪",
            notes="Weekly shopping",
        )

        assert expense.id is not None
        assert expense.business == "SuperSal"
        assert expense.notes == "Weekly shopping"


class TestExpenseRepositoryGet:
    """Tests for ExpenseRepository.get()"""

    def test_get_existing_expense(self, db_session):
        """Test retrieving an existing expense by ID."""
        repo = ExpenseRepository(db_session)

        created = repo.create(
            date=date(2025, 12, 1),
            category="Transport",
            amount=Decimal("15.00"),
            account="Cash",
            currency="₪",
        )

        retrieved = repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.category == "Transport"
        assert retrieved.amount == Decimal("15.00")

    def test_get_nonexistent_expense(self, db_session):
        """Test retrieving a non-existent expense returns None."""
        repo = ExpenseRepository(db_session)

        result = repo.get(99999)

        assert result is None


class TestExpenseRepositoryList:
    """Tests for ExpenseRepository.list()"""

    def test_list_all_expenses(self, db_session):
        """Test listing all expenses."""
        repo = ExpenseRepository(db_session)

        # Create test data
        repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Transport",
            amount=Decimal("20.00"),
            account="Cash",
            currency="₪",
        )

        expenses = repo.list()

        assert len(expenses) == 2

    def test_list_with_pagination(self, db_session):
        """Test listing expenses with pagination."""
        repo = ExpenseRepository(db_session)

        # Create 5 expenses
        for i in range(5):
            repo.create(
                date=date(2025, 12, i + 1),
                category="Test",
                amount=Decimal("10.00"),
                account="Test",
                currency="₪",
            )

        # Get first 2
        page1 = repo.list(skip=0, limit=2)
        assert len(page1) == 2

        # Get next 2
        page2 = repo.list(skip=2, limit=2)
        assert len(page2) == 2

        # Get remaining
        page3 = repo.list(skip=4, limit=2)
        assert len(page3) == 1

    def test_list_with_filter(self, db_session):
        """Test listing expenses with filter."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Transport",
            amount=Decimal("20.00"),
            account="Cash",
            currency="₪",
        )

        groceries = repo.list(category="Groceries")

        assert len(groceries) == 1
        assert groceries[0].category == "Groceries"

    def test_list_empty_database(self, db_session):
        """Test listing from empty database returns empty list."""
        repo = ExpenseRepository(db_session)

        expenses = repo.list()

        assert expenses == []


class TestExpenseRepositoryUpdate:
    """Tests for ExpenseRepository.update()"""

    def test_update_expense_field(self, db_session):
        """Test updating a single field of an expense."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )

        updated = repo.update(expense.id, amount=Decimal("150.00"))

        assert updated is not None
        assert updated.amount == Decimal("150.00")
        assert updated.category == "Groceries"  # Other fields unchanged

    def test_update_multiple_fields(self, db_session):
        """Test updating multiple fields at once."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )

        updated = repo.update(
            expense.id,
            amount=Decimal("150.00"),
            category="Food",
            notes="Updated notes",
        )

        assert updated.amount == Decimal("150.00")
        assert updated.category == "Food"
        assert updated.notes == "Updated notes"

    def test_update_nonexistent_expense(self, db_session):
        """Test updating a non-existent expense returns None."""
        repo = ExpenseRepository(db_session)

        result = repo.update(99999, amount=Decimal("100.00"))

        assert result is None


class TestExpenseRepositoryDelete:
    """Tests for ExpenseRepository.delete()"""

    def test_delete_existing_expense(self, db_session):
        """Test deleting an existing expense."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )

        result = repo.delete(expense.id)

        assert result is True
        assert repo.get(expense.id) is None

    def test_delete_nonexistent_expense(self, db_session):
        """Test deleting a non-existent expense returns False."""
        repo = ExpenseRepository(db_session)

        result = repo.delete(99999)

        assert result is False


class TestExpenseRepositoryBulkDelete:
    """Tests for ExpenseRepository.bulk_delete()"""

    def test_bulk_delete_multiple_expenses(self, db_session):
        """Test deleting multiple expenses at once."""
        repo = ExpenseRepository(db_session)

        # Create test expenses
        exp1 = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        exp2 = repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        exp3 = repo.create(
            date=date(2025, 12, 3),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )

        # Store IDs before deletion
        id1, id2, id3 = exp1.id, exp2.id, exp3.id

        # Delete 2 of them
        deleted_count = repo.bulk_delete([id1, id2])

        assert deleted_count == 2
        assert repo.get(id1) is None
        assert repo.get(id2) is None
        assert repo.get(id3) is not None

    def test_bulk_delete_nonexistent_ids(self, db_session):
        """Test bulk delete with non-existent IDs."""
        repo = ExpenseRepository(db_session)

        deleted_count = repo.bulk_delete([99998, 99999])

        assert deleted_count == 0

    def test_bulk_delete_mixed_ids(self, db_session):
        """Test bulk delete with mix of existing and non-existent IDs."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )

        deleted_count = repo.bulk_delete([expense.id, 99999])

        assert deleted_count == 1


class TestExpenseRepositoryCount:
    """Tests for ExpenseRepository.count()"""

    def test_count_all_expenses(self, db_session):
        """Test counting all expenses."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )

        count = repo.count()

        assert count == 2

    def test_count_with_filter(self, db_session):
        """Test counting expenses with filter."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Transport",
            amount=Decimal("20.00"),
            account="Cash",
            currency="₪",
        )

        count = repo.count(category="Groceries")

        assert count == 1


class TestExpenseRepositoryExists:
    """Tests for ExpenseRepository.exists()"""

    def test_exists_returns_true_for_existing(self, db_session):
        """Test exists returns True for existing expense."""
        repo = ExpenseRepository(db_session)

        expense = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )

        assert repo.exists(expense.id) is True

    def test_exists_returns_false_for_nonexistent(self, db_session):
        """Test exists returns False for non-existent expense."""
        repo = ExpenseRepository(db_session)

        assert repo.exists(99999) is False


class TestExpenseRepositoryDateRange:
    """Tests for ExpenseRepository.get_by_date_range()"""

    def test_get_expenses_in_date_range(self, db_session):
        """Test getting expenses within a date range."""
        repo = ExpenseRepository(db_session)

        # Create expenses across different dates
        repo.create(
            date=date(2025, 11, 30),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 5),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 15),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 25),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )

        # Get expenses in December 1-20
        expenses = repo.get_by_date_range(date(2025, 12, 1), date(2025, 12, 20))

        assert len(expenses) == 2
        # Should be ordered by date descending
        assert expenses[0].date == date(2025, 12, 15)
        assert expenses[1].date == date(2025, 12, 5)


class TestExpenseRepositoryCategory:
    """Tests for category-related methods"""

    def test_get_by_category(self, db_session):
        """Test getting expenses by category."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Groceries",
            amount=Decimal("50.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 3),
            category="Transport",
            amount=Decimal("20.00"),
            account="Cash",
            currency="₪",
        )

        groceries = repo.get_by_category("Groceries")

        assert len(groceries) == 2
        assert all(e.category == "Groceries" for e in groceries)

    def test_get_total_by_category(self, db_session):
        """Test calculating total amount by category."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Groceries",
            amount=Decimal("50.50"),
            account="Visa",
            currency="₪",
        )

        total = repo.get_total_by_category("Groceries")

        assert total == Decimal("150.50")

    def test_get_total_by_category_empty(self, db_session):
        """Test total by category returns zero when no expenses."""
        repo = ExpenseRepository(db_session)

        total = repo.get_total_by_category("NonExistent")

        assert total == Decimal("0")

    def test_get_all_categories(self, db_session):
        """Test getting all unique categories."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Transport",
            amount=Decimal("20.00"),
            account="Cash",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 3),
            category="Groceries",
            amount=Decimal("50.00"),
            account="Visa",
            currency="₪",
        )

        categories = repo.get_all_categories()

        assert len(categories) == 2
        assert "Groceries" in categories
        assert "Transport" in categories


class TestExpenseRepositoryAccount:
    """Tests for account-related methods"""

    def test_get_by_account(self, db_session):
        """Test getting expenses by account."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("50.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 3),
            category="Test",
            amount=Decimal("20.00"),
            account="Cash",
            currency="₪",
        )

        visa_expenses = repo.get_by_account("Visa")

        assert len(visa_expenses) == 2
        assert all(e.account == "Visa" for e in visa_expenses)

    def test_get_all_accounts(self, db_session):
        """Test getting all unique accounts."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("50.00"),
            account="Cash",
            currency="₪",
        )

        accounts = repo.get_all_accounts()

        assert len(accounts) == 2
        assert "Visa" in accounts
        assert "Cash" in accounts


class TestExpenseRepositorySearch:
    """Tests for search methods"""

    def test_search_by_business(self, db_session):
        """Test searching expenses by business name."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            business="SuperSal",
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            business="Super Pharm",
            category="Health",
            amount=Decimal("50.00"),
            account="Visa",
            currency="₪",
        )

        results = repo.search_by_business("Super")

        assert len(results) == 2

    def test_search_by_business_case_insensitive(self, db_session):
        """Test business search is case-insensitive."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            business="SuperSal",
            category="Groceries",
            amount=Decimal("100.00"),
            account="Visa",
            currency="₪",
        )

        results = repo.search_by_business("supersal")

        assert len(results) == 1


class TestExpenseRepositoryRecent:
    """Tests for get_recent method"""

    def test_get_recent_expenses(self, db_session):
        """Test getting most recent expenses."""
        repo = ExpenseRepository(db_session)

        # Create expenses with different dates
        for i in range(15):
            repo.create(
                date=date(2025, 12, i + 1),
                category="Test",
                amount=Decimal("100.00"),
                account="Test",
                currency="₪",
            )

        recent = repo.get_recent(limit=10)

        assert len(recent) == 10
        # Should be ordered by date descending
        assert recent[0].date == date(2025, 12, 15)
        assert recent[9].date == date(2025, 12, 6)


class TestExpenseRepositoryTotalByDateRange:
    """Tests for get_total_by_date_range method"""

    def test_get_total_in_date_range(self, db_session):
        """Test calculating total expenses in date range."""
        repo = ExpenseRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("100.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 5),
            category="Test",
            amount=Decimal("50.50"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 15),
            category="Test",
            amount=Decimal("25.25"),
            account="Test",
            currency="₪",
        )

        total = repo.get_total_by_date_range(date(2025, 12, 1), date(2025, 12, 10))

        assert total == Decimal("150.50")

    def test_get_total_empty_date_range(self, db_session):
        """Test total returns zero for date range with no expenses."""
        repo = ExpenseRepository(db_session)

        total = repo.get_total_by_date_range(date(2025, 1, 1), date(2025, 1, 31))

        assert total == Decimal("0")
