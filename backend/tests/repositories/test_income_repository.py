"""Tests for IncomeRepository."""

from datetime import date
from decimal import Decimal

import pytest

from app.repositories.income_repository import IncomeRepository


class TestIncomeRepositoryCreate:
    """Tests for IncomeRepository.create()"""

    def test_create_minimal_income(self, db_session):
        """Test creating an income with minimal required fields."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank Account",
            currency="₪",
        )

        assert income.id is not None
        assert income.date == date(2025, 12, 1)
        assert income.category == "Salary"
        assert income.amount == Decimal("5000.00")
        assert income.account == "Bank Account"
        assert income.currency == "₪"
        assert income.notes is None

    def test_create_full_income(self, db_session):
        """Test creating an income with all fields."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank Account",
            currency="₪",
            notes="Monthly salary",
        )

        assert income.id is not None
        assert income.notes == "Monthly salary"


class TestIncomeRepositoryGet:
    """Tests for IncomeRepository.get()"""

    def test_get_existing_income(self, db_session):
        """Test retrieving an existing income by ID."""
        repo = IncomeRepository(db_session)

        created = repo.create(
            date=date(2025, 12, 1),
            category="Freelance",
            amount=Decimal("1500.00"),
            account="PayPal",
            currency="₪",
        )

        retrieved = repo.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.category == "Freelance"
        assert retrieved.amount == Decimal("1500.00")

    def test_get_nonexistent_income(self, db_session):
        """Test retrieving a non-existent income returns None."""
        repo = IncomeRepository(db_session)

        result = repo.get(99999)

        assert result is None


class TestIncomeRepositoryList:
    """Tests for IncomeRepository.list()"""

    def test_list_all_incomes(self, db_session):
        """Test listing all income records."""
        repo = IncomeRepository(db_session)

        # Create test data
        repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Freelance",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )

        incomes = repo.list()

        assert len(incomes) == 2

    def test_list_with_pagination(self, db_session):
        """Test listing income records with pagination."""
        repo = IncomeRepository(db_session)

        # Create 5 income records
        for i in range(5):
            repo.create(
                date=date(2025, 12, i + 1),
                category="Test",
                amount=Decimal("100.00"),
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
        """Test listing income records with filter."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Freelance",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )

        salary_income = repo.list(category="Salary")

        assert len(salary_income) == 1
        assert salary_income[0].category == "Salary"

    def test_list_empty_database(self, db_session):
        """Test listing from empty database returns empty list."""
        repo = IncomeRepository(db_session)

        incomes = repo.list()

        assert incomes == []


class TestIncomeRepositoryUpdate:
    """Tests for IncomeRepository.update()"""

    def test_update_income_field(self, db_session):
        """Test updating a single field of an income."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )

        updated = repo.update(income.id, amount=Decimal("5500.00"))

        assert updated is not None
        assert updated.amount == Decimal("5500.00")
        assert updated.category == "Salary"  # Other fields unchanged

    def test_update_multiple_fields(self, db_session):
        """Test updating multiple fields at once."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )

        updated = repo.update(
            income.id,
            amount=Decimal("5500.00"),
            category="Bonus",
            notes="Year-end bonus",
        )

        assert updated.amount == Decimal("5500.00")
        assert updated.category == "Bonus"
        assert updated.notes == "Year-end bonus"

    def test_update_nonexistent_income(self, db_session):
        """Test updating a non-existent income returns None."""
        repo = IncomeRepository(db_session)

        result = repo.update(99999, amount=Decimal("1000.00"))

        assert result is None


class TestIncomeRepositoryDelete:
    """Tests for IncomeRepository.delete()"""

    def test_delete_existing_income(self, db_session):
        """Test deleting an existing income."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )

        result = repo.delete(income.id)

        assert result is True
        assert repo.get(income.id) is None

    def test_delete_nonexistent_income(self, db_session):
        """Test deleting a non-existent income returns False."""
        repo = IncomeRepository(db_session)

        result = repo.delete(99999)

        assert result is False


class TestIncomeRepositoryBulkDelete:
    """Tests for IncomeRepository.bulk_delete()"""

    def test_bulk_delete_multiple_incomes(self, db_session):
        """Test deleting multiple income records at once."""
        repo = IncomeRepository(db_session)

        # Create test income records
        inc1 = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )
        inc2 = repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )
        inc3 = repo.create(
            date=date(2025, 12, 3),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )

        # Store IDs before deletion
        id1, id2, id3 = inc1.id, inc2.id, inc3.id

        # Delete 2 of them
        deleted_count = repo.bulk_delete([id1, id2])

        assert deleted_count == 2
        assert repo.get(id1) is None
        assert repo.get(id2) is None
        assert repo.get(id3) is not None

    def test_bulk_delete_nonexistent_ids(self, db_session):
        """Test bulk delete with non-existent IDs."""
        repo = IncomeRepository(db_session)

        deleted_count = repo.bulk_delete([99998, 99999])

        assert deleted_count == 0

    def test_bulk_delete_mixed_ids(self, db_session):
        """Test bulk delete with mix of existing and non-existent IDs."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )

        deleted_count = repo.bulk_delete([income.id, 99999])

        assert deleted_count == 1


class TestIncomeRepositoryCount:
    """Tests for IncomeRepository.count()"""

    def test_count_all_incomes(self, db_session):
        """Test counting all income records."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )

        count = repo.count()

        assert count == 2

    def test_count_with_filter(self, db_session):
        """Test counting income records with filter."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Freelance",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )

        count = repo.count(category="Salary")

        assert count == 1


class TestIncomeRepositoryExists:
    """Tests for IncomeRepository.exists()"""

    def test_exists_returns_true_for_existing(self, db_session):
        """Test exists returns True for existing income."""
        repo = IncomeRepository(db_session)

        income = repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )

        assert repo.exists(income.id) is True

    def test_exists_returns_false_for_nonexistent(self, db_session):
        """Test exists returns False for non-existent income."""
        repo = IncomeRepository(db_session)

        assert repo.exists(99999) is False


class TestIncomeRepositoryDateRange:
    """Tests for IncomeRepository.get_by_date_range()"""

    def test_get_incomes_in_date_range(self, db_session):
        """Test getting income records within a date range."""
        repo = IncomeRepository(db_session)

        # Create incomes across different dates
        repo.create(
            date=date(2025, 11, 30),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 5),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 15),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 25),
            category="Test",
            amount=Decimal("1000.00"),
            account="Test",
            currency="₪",
        )

        # Get incomes in December 1-20
        incomes = repo.get_by_date_range(date(2025, 12, 1), date(2025, 12, 20))

        assert len(incomes) == 2
        # Should be ordered by date descending
        assert incomes[0].date == date(2025, 12, 15)
        assert incomes[1].date == date(2025, 12, 5)


class TestIncomeRepositoryCategory:
    """Tests for category-related methods"""

    def test_get_by_category(self, db_session):
        """Test getting income records by category."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 3),
            category="Freelance",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )

        salary = repo.get_by_category("Salary")

        assert len(salary) == 2
        assert all(i.category == "Salary" for i in salary)

    def test_get_total_by_category(self, db_session):
        """Test calculating total income amount by category."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Salary",
            amount=Decimal("5500.00"),
            account="Bank",
            currency="₪",
        )

        total = repo.get_total_by_category("Salary")

        assert total == Decimal("10500.00")

    def test_get_total_by_category_empty(self, db_session):
        """Test total by category returns zero when no income."""
        repo = IncomeRepository(db_session)

        total = repo.get_total_by_category("NonExistent")

        assert total == Decimal("0")

    def test_get_all_categories(self, db_session):
        """Test getting all unique categories."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Freelance",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 3),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )

        categories = repo.get_all_categories()

        assert len(categories) == 2
        assert "Salary" in categories
        assert "Freelance" in categories


class TestIncomeRepositoryAccount:
    """Tests for account-related methods"""

    def test_get_by_account(self, db_session):
        """Test getting income records by account."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 3),
            category="Test",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )

        bank_incomes = repo.get_by_account("Bank")

        assert len(bank_incomes) == 2
        assert all(i.account == "Bank" for i in bank_incomes)

    def test_get_all_accounts(self, db_session):
        """Test getting all unique accounts."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 2),
            category="Test",
            amount=Decimal("1000.00"),
            account="PayPal",
            currency="₪",
        )

        accounts = repo.get_all_accounts()

        assert len(accounts) == 2
        assert "Bank" in accounts
        assert "PayPal" in accounts


class TestIncomeRepositoryRecent:
    """Tests for get_recent method"""

    def test_get_recent_incomes(self, db_session):
        """Test getting most recent income records."""
        repo = IncomeRepository(db_session)

        # Create income records with different dates
        for i in range(15):
            repo.create(
                date=date(2025, 12, i + 1),
                category="Test",
                amount=Decimal("1000.00"),
                account="Test",
                currency="₪",
            )

        recent = repo.get_recent(limit=10)

        assert len(recent) == 10
        # Should be ordered by date descending
        assert recent[0].date == date(2025, 12, 15)
        assert recent[9].date == date(2025, 12, 6)


class TestIncomeRepositoryTotalByDateRange:
    """Tests for get_total_by_date_range method"""

    def test_get_total_in_date_range(self, db_session):
        """Test calculating total income in date range."""
        repo = IncomeRepository(db_session)

        repo.create(
            date=date(2025, 12, 1),
            category="Test",
            amount=Decimal("5000.00"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 5),
            category="Test",
            amount=Decimal("1000.50"),
            account="Test",
            currency="₪",
        )
        repo.create(
            date=date(2025, 12, 15),
            category="Test",
            amount=Decimal("500.25"),
            account="Test",
            currency="₪",
        )

        total = repo.get_total_by_date_range(date(2025, 12, 1), date(2025, 12, 10))

        assert total == Decimal("6000.50")

    def test_get_total_empty_date_range(self, db_session):
        """Test total returns zero for date range with no income."""
        repo = IncomeRepository(db_session)

        total = repo.get_total_by_date_range(date(2025, 1, 1), date(2025, 1, 31))

        assert total == Decimal("0")
