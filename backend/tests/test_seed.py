"""
Tests for the seed script functionality.
Uses SQLite in-memory database to validate the seeding logic.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models import Base, Expense, Income
from scripts.seed import (
    load_json_fixture,
    parse_date,
    seed_expenses,
    seed_incomes,
    verify_counts,
)


def test_parse_date():
    """Test date parsing from string."""
    result = parse_date("2025-11-01")
    assert result == date(2025, 11, 1)


def test_load_json_fixture_expenses():
    """Test loading expenses fixture."""
    expenses = load_json_fixture("expenses.json")
    assert isinstance(expenses, list)
    assert len(expenses) > 0
    # Check first expense has expected fields
    first = expenses[0]
    assert "id" in first
    assert "date" in first
    assert "category" in first
    assert "amount" in first
    assert "account" in first


def test_load_json_fixture_incomes():
    """Test loading incomes fixture."""
    incomes = load_json_fixture("incomes.json")
    assert isinstance(incomes, list)
    assert len(incomes) > 0
    # Check first income has expected fields
    first = incomes[0]
    assert "id" in first
    assert "date" in first
    assert "category" in first
    assert "amount" in first
    assert "account" in first


def test_load_json_fixture_nonexistent():
    """Test loading a non-existent fixture returns empty list."""
    result = load_json_fixture("nonexistent.json")
    assert result == []


def test_seed_expenses_sqlite():
    """Test seeding expenses to an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Sample expense data
    expenses_data = [
        {
            "id": 1,
            "date": "2025-11-01",
            "business": "Test Business",
            "category": "Food",
            "amount": 100.50,
            "account": "Cash",
            "currency": "₪",
            "notes": "Test note"
        },
        {
            "id": 2,
            "date": "2025-11-02",
            "business": None,
            "category": "Transport",
            "amount": 25.00,
            "account": "Card",
            "currency": "₪",
            "notes": ""
        }
    ]
    
    count = seed_expenses(session, expenses_data)
    session.commit()
    
    assert count == 2
    
    # Verify data was inserted
    result = session.execute(text("SELECT COUNT(*) FROM expenses")).scalar()
    assert result == 2
    
    session.close()


def test_seed_incomes_sqlite():
    """Test seeding incomes to an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Sample income data
    incomes_data = [
        {
            "id": 1,
            "date": "2025-11-01",
            "category": "Salary",
            "amount": 5000.00,
            "account": "Bank",
            "currency": "₪",
            "notes": "Monthly"
        }
    ]
    
    count = seed_incomes(session, incomes_data)
    session.commit()
    
    assert count == 1
    
    # Verify data was inserted
    result = session.execute(text("SELECT COUNT(*) FROM incomes")).scalar()
    assert result == 1
    
    session.close()


def test_verify_counts():
    """Test row count verification."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Add some data
    session.add(Expense(
        id=1,
        date=date(2025, 11, 1),
        category="Food",
        amount=Decimal("100.00"),
        account="Cash",
        currency="₪"
    ))
    session.add(Income(
        id=1,
        date=date(2025, 11, 1),
        category="Salary",
        amount=Decimal("5000.00"),
        account="Bank",
        currency="₪"
    ))
    session.commit()
    
    # Verify counts - should pass
    assert verify_counts(session, 1, 1) is True
    
    # Verify counts - should fail (expected more)
    assert verify_counts(session, 5, 5) is False
    
    session.close()


def test_seed_from_actual_fixtures():
    """Test seeding from the actual fixture files."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Load actual fixtures
    expenses_data = load_json_fixture("expenses.json")
    incomes_data = load_json_fixture("incomes.json")
    
    # Seed
    expense_count = seed_expenses(session, expenses_data)
    income_count = seed_incomes(session, incomes_data)
    session.commit()
    
    # Verify counts match fixture counts
    assert expense_count == len(expenses_data)
    assert income_count == len(incomes_data)
    
    # Verify database has correct counts
    assert verify_counts(session, len(expenses_data), len(incomes_data)) is True
    
    session.close()
