"""Seed minimal test data for smoke integration tests.

This script creates sample expense and income records in the database
for use in smoke tests. It's designed to be run after alembic migrations
have been applied to a clean database.

Usage:
    poetry run python scripts/seed_test_data.py
"""

import os
import sys
from datetime import date
from decimal import Decimal

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Expense, Income


def get_database_url() -> str:
    """Get database URL from environment."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://test_user:test_password@localhost:5432/test_db"
    )


def seed_data():
    """Seed the database with minimal test data."""
    database_url = get_database_url()
    print(f"Connecting to database...")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if data already exists
        existing_expenses = session.query(Expense).count()
        existing_incomes = session.query(Income).count()

        if existing_expenses > 0 or existing_incomes > 0:
            print(f"Data already exists (expenses: {existing_expenses}, incomes: {existing_incomes}). Skipping seed.")
            return

        # Create sample expenses
        expenses = [
            Expense(
                date=date(2025, 1, 15),
                business="Test Supermarket",
                category="Groceries",
                amount=Decimal("150.50"),
                account="Credit Card",
                currency="₪",
                notes="Weekly groceries for smoke test",
            ),
            Expense(
                date=date(2025, 1, 20),
                business="Test Gas Station",
                category="Transport",
                amount=Decimal("200.00"),
                account="Debit Card",
                currency="₪",
                notes="Fuel for smoke test",
            ),
        ]

        # Create sample incomes
        incomes = [
            Income(
                date=date(2025, 1, 1),
                category="Salary",
                amount=Decimal("10000.00"),
                account="Bank Account",
                currency="₪",
                notes="Monthly salary for smoke test",
            ),
            Income(
                date=date(2025, 1, 15),
                category="Freelance",
                amount=Decimal("2500.00"),
                account="PayPal",
                currency="₪",
                notes="Freelance project for smoke test",
            ),
        ]

        # Add all records
        session.add_all(expenses)
        session.add_all(incomes)
        session.commit()

        print(f"✓ Seeded {len(expenses)} expenses and {len(incomes)} incomes")

    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()
