"""
Test that the schema models work correctly with an in-memory SQLite database.
This validates the migration schema without requiring a running PostgreSQL server.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import Base, Expense, Income


def test_expense_model_crud():
    """Verify Expense model can be created, queried, and deleted."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create
    expense = Expense(
        date=date(2025, 11, 1),
        business="Test Business",
        category="Groceries",
        amount=Decimal("150.75"),
        account="Cash",
        currency="₪",
        notes="Test expense"
    )
    session.add(expense)
    session.commit()

    # Read
    result = session.execute(select(Expense).where(Expense.id == expense.id)).scalar_one()
    assert result.date == date(2025, 11, 1)
    assert result.business == "Test Business"
    assert result.category == "Groceries"
    assert result.amount == Decimal("150.75")
    assert result.account == "Cash"
    assert result.currency == "₪"
    assert result.notes == "Test expense"

    # Delete
    session.delete(result)
    session.commit()
    assert session.execute(select(Expense)).first() is None

    session.close()


def test_income_model_crud():
    """Verify Income model can be created, queried, and deleted."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create
    income = Income(
        date=date(2025, 11, 1),
        category="Salary",
        amount=Decimal("8000.00"),
        account="Bank Account",
        currency="₪",
        notes="Monthly salary"
    )
    session.add(income)
    session.commit()

    # Read
    result = session.execute(select(Income).where(Income.id == income.id)).scalar_one()
    assert result.date == date(2025, 11, 1)
    assert result.category == "Salary"
    assert result.amount == Decimal("8000.00")
    assert result.account == "Bank Account"
    assert result.currency == "₪"
    assert result.notes == "Monthly salary"

    # Delete
    session.delete(result)
    session.commit()
    assert session.execute(select(Income)).first() is None

    session.close()


def test_expense_optional_fields():
    """Verify Expense model handles optional fields correctly."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create with minimal required fields
    expense = Expense(
        date=date(2025, 11, 1),
        category="Food",
        amount=Decimal("25.00"),
        account="Cash",
        currency="₪"
        # business and notes are optional
    )
    session.add(expense)
    session.commit()

    result = session.execute(select(Expense).where(Expense.id == expense.id)).scalar_one()
    assert result.business is None
    assert result.notes is None

    session.close()


def test_income_optional_fields():
    """Verify Income model handles optional fields correctly."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create with minimal required fields
    income = Income(
        date=date(2025, 11, 1),
        category="Bonus",
        amount=Decimal("500.00"),
        account="Bank",
        currency="₪"
        # notes is optional
    )
    session.add(income)
    session.commit()

    result = session.execute(select(Income).where(Income.id == income.id)).scalar_one()
    assert result.notes is None

    session.close()
