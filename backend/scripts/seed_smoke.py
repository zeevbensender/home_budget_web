"""Idempotent seed script for smoke integration tests.

This script loads test data from JSON fixtures and seeds the database
for smoke testing. It is designed to be idempotent - running it multiple
times will not create duplicate data.

Usage:
    poetry run python scripts/seed_smoke.py

    Or with make:
    make seed-smoke
"""

import json
import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Expense, Income


def get_database_url() -> str:
    """Get database URL from environment.

    Default matches docker-compose-postgres.yaml for local development.
    CI workflow uses different credentials via environment variable.
    """
    return os.getenv(
        "DATABASE_URL", "postgresql://poc_user:poc_password@localhost:5432/poc_db"
    )


def load_fixture(fixture_name: str) -> list[dict]:
    """Load JSON fixture file from fixtures directory."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixture_path = fixtures_dir / f"{fixture_name}.json"

    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_date(date_str: str) -> date:
    """Parse ISO date string to date object."""
    return date.fromisoformat(date_str)


def seed_expenses(session, expenses_data: list[dict]) -> int:
    """Seed expenses from fixture data. Returns count of records added."""
    added = 0
    for item in expenses_data:
        # Check if expense already exists (by date, business, and amount)
        existing = (
            session.query(Expense)
            .filter(
                Expense.date == parse_date(item["date"]),
                Expense.business == item["business"],
                Expense.amount == Decimal(item["amount"]),
            )
            .first()
        )

        if existing:
            continue

        expense = Expense(
            date=parse_date(item["date"]),
            business=item["business"],
            category=item["category"],
            amount=Decimal(item["amount"]),
            account=item["account"],
            currency=item["currency"],
            notes=item.get("notes"),
        )
        session.add(expense)
        added += 1

    return added


def seed_incomes(session, incomes_data: list[dict]) -> int:
    """Seed incomes from fixture data. Returns count of records added."""
    added = 0
    for item in incomes_data:
        # Check if income already exists (by date, category, and amount)
        existing = (
            session.query(Income)
            .filter(
                Income.date == parse_date(item["date"]),
                Income.category == item["category"],
                Income.amount == Decimal(item["amount"]),
            )
            .first()
        )

        if existing:
            continue

        income = Income(
            date=parse_date(item["date"]),
            category=item["category"],
            amount=Decimal(item["amount"]),
            account=item["account"],
            currency=item["currency"],
            notes=item.get("notes"),
        )
        session.add(income)
        added += 1

    return added


def seed_smoke_data():
    """Seed the database with smoke test data from JSON fixtures.

    This function is idempotent - it checks for existing data before
    inserting new records.
    """
    database_url = get_database_url()
    print("Connecting to database...")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Load fixtures
        expenses_data = load_fixture("expenses")
        incomes_data = load_fixture("incomes")

        print(
            f"Loaded {len(expenses_data)} expenses and {len(incomes_data)} incomes from fixtures"
        )

        # Seed data
        expenses_added = seed_expenses(session, expenses_data)
        incomes_added = seed_incomes(session, incomes_data)

        session.commit()

        if expenses_added == 0 and incomes_added == 0:
            print("✓ No new data added (all records already exist)")
        else:
            print(f"✓ Seeded {expenses_added} expenses and {incomes_added} incomes")

        # Report totals
        total_expenses = session.query(Expense).count()
        total_incomes = session.query(Income).count()
        print(
            f"  Total in database: {total_expenses} expenses, {total_incomes} incomes"
        )

    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_smoke_data()
