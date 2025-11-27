#!/usr/bin/env python
"""
Seed script that loads JSON fixtures into Postgres.

This script reads the existing expense and income JSON files and inserts
the data into the PostgreSQL database.

Usage:
    DATABASE_URL=postgresql://user:pass@localhost/db python -m scripts.seed
    # or
    cd backend && python -m scripts.seed
"""

import json
import os
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import Base, Expense, Income


def get_database_url() -> str:
    """Get database URL from environment variable."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Example: DATABASE_URL=postgresql://budget:budget@localhost:5432/budget_db"
        )
    return url


def load_json_fixture(filename: str) -> list[dict]:
    """Load JSON fixture from the app/data directory."""
    data_dir = Path(__file__).parent.parent / "app" / "data"
    filepath = data_dir / filename
    
    if not filepath.exists():
        print(f"Warning: {filepath} not found, using empty list")
        return []
    
    with open(filepath, "r") as f:
        return json.load(f)


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def seed_expenses(session, expenses_data: list[dict]) -> int:
    """Seed expenses table from JSON data."""
    count = 0
    for item in expenses_data:
        expense = Expense(
            id=item["id"],
            date=parse_date(item["date"]),
            business=item.get("business"),
            category=item["category"],
            amount=Decimal(str(item["amount"])),
            account=item["account"],
            currency=item.get("currency", "₪"),
            notes=item.get("notes") or None
        )
        session.merge(expense)  # Use merge to handle existing records
        count += 1
    return count


def seed_incomes(session, incomes_data: list[dict]) -> int:
    """Seed incomes table from JSON data."""
    count = 0
    for item in incomes_data:
        income = Income(
            id=item["id"],
            date=parse_date(item["date"]),
            category=item["category"],
            amount=Decimal(str(item["amount"])),
            account=item["account"],
            currency=item.get("currency", "₪"),
            notes=item.get("notes") or None
        )
        session.merge(income)  # Use merge to handle existing records
        count += 1
    return count


def verify_counts(session, expected_expenses: int, expected_incomes: int) -> bool:
    """Verify that the row counts match expected fixture counts."""
    expense_count = session.execute(text("SELECT COUNT(*) FROM expenses")).scalar()
    income_count = session.execute(text("SELECT COUNT(*) FROM incomes")).scalar()
    
    print(f"Expenses: expected={expected_expenses}, actual={expense_count}")
    print(f"Incomes: expected={expected_incomes}, actual={income_count}")
    
    return expense_count >= expected_expenses and income_count >= expected_incomes


def main():
    """Main entry point for the seed script."""
    print("=" * 50)
    print("Home Budget Web - Seed Script")
    print("=" * 50)
    
    # Get database URL
    try:
        database_url = get_database_url()
        # Mask password for display
        masked_url = database_url
        if "@" in masked_url:
            parts = masked_url.split("@")
            user_pass = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                masked_url = parts[0].split("://")[0] + f"://{user}:****@" + parts[1]
        print(f"Database: {masked_url}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Ensure tables exist
        print("\nCreating tables if they don't exist...")
        Base.metadata.create_all(engine)
        
        # Load fixtures
        print("\nLoading JSON fixtures...")
        expenses_data = load_json_fixture("expenses.json")
        incomes_data = load_json_fixture("incomes.json")
        
        print(f"Found {len(expenses_data)} expenses in fixtures")
        print(f"Found {len(incomes_data)} incomes in fixtures")
        
        # Seed data
        print("\nSeeding database...")
        expense_count = seed_expenses(session, expenses_data)
        income_count = seed_incomes(session, incomes_data)
        session.commit()
        
        print(f"Inserted/updated {expense_count} expenses")
        print(f"Inserted/updated {income_count} incomes")
        
        # Verify counts
        print("\nVerifying row counts...")
        if verify_counts(session, len(expenses_data), len(incomes_data)):
            print("\n✓ Seed completed successfully!")
            return 0
        else:
            print("\n✗ Row count verification failed!")
            return 1
            
    except Exception as e:
        print(f"\nError: {e}")
        session.rollback()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
