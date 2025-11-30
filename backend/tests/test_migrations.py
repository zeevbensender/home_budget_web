"""Test migration and schema setup."""

from decimal import Decimal

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import (Expense,  # noqa: F401 - needed for model registration
                        Income)


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test session with tables created."""
    # Create all tables from metadata
    Base.metadata.create_all(test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()
    yield session
    session.close()


class TestMigrationSchema:
    """Tests for database schema created by migrations."""

    def test_tables_created(self, test_engine):
        """Verify that expenses and incomes tables are created."""
        # Create tables
        Base.metadata.create_all(test_engine)

        inspector = inspect(test_engine)
        table_names = inspector.get_table_names()

        assert "expenses" in table_names
        assert "incomes" in table_names

    def test_expenses_table_columns(self, test_engine):
        """Verify expenses table has all required columns."""
        Base.metadata.create_all(test_engine)

        inspector = inspect(test_engine)
        columns = {col["name"] for col in inspector.get_columns("expenses")}

        expected_columns = {
            "id",
            "date",
            "business",
            "category",
            "amount",
            "account",
            "currency",
            "notes",
        }
        assert expected_columns == columns

    def test_incomes_table_columns(self, test_engine):
        """Verify incomes table has all required columns."""
        Base.metadata.create_all(test_engine)

        inspector = inspect(test_engine)
        columns = {col["name"] for col in inspector.get_columns("incomes")}

        expected_columns = {
            "id",
            "date",
            "category",
            "amount",
            "account",
            "currency",
            "notes",
        }
        assert expected_columns == columns

    def test_expense_model_crud(self, test_session):
        """Test basic CRUD operations on Expense model."""
        from datetime import date

        # Create
        expense = Expense(
            date=date(2025, 11, 1),
            business="Test Business",
            category="Test Category",
            amount=Decimal("100.50"),
            account="Test Account",
            currency="₪",
            notes="Test notes",
        )
        test_session.add(expense)
        test_session.commit()

        # Read
        fetched = test_session.query(Expense).first()
        assert fetched is not None
        assert fetched.business == "Test Business"
        assert fetched.amount == Decimal("100.50")

        # Update
        fetched.amount = Decimal("200.00")
        test_session.commit()

        updated = test_session.query(Expense).first()
        assert updated.amount == Decimal("200.00")

        # Delete
        test_session.delete(fetched)
        test_session.commit()

        deleted = test_session.query(Expense).first()
        assert deleted is None

    def test_income_model_crud(self, test_session):
        """Test basic CRUD operations on Income model."""
        from datetime import date

        # Create
        income = Income(
            date=date(2025, 11, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
            notes="Monthly salary",
        )
        test_session.add(income)
        test_session.commit()

        # Read
        fetched = test_session.query(Income).first()
        assert fetched is not None
        assert fetched.category == "Salary"
        assert fetched.amount == Decimal("5000.00")

        # Update
        fetched.amount = Decimal("5500.00")
        test_session.commit()

        updated = test_session.query(Income).first()
        assert updated.amount == Decimal("5500.00")

        # Delete
        test_session.delete(fetched)
        test_session.commit()

        deleted = test_session.query(Income).first()
        assert deleted is None
