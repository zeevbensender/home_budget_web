#!/usr/bin/env python
"""
Seed script for Home Budget Web database.
Loads sample data into the PostgreSQL database.
"""
import os
import sys

# Add the backend directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import Expense, Income


SEED_EXPENSES = [
    {
        "date": "2025-11-01",
        "business": "SuperSal",
        "category": "Groceries",
        "amount": 142.50,
        "account": "Visa 1234",
        "currency": "₪",
        "notes": "Weekly shopping",
    },
    {
        "date": "2025-11-05",
        "business": "Rav-Kav",
        "category": "Transport",
        "amount": 15.00,
        "account": "Cash",
        "currency": "₪",
        "notes": "Bus to work",
    },
    {
        "date": "2025-11-10",
        "business": "Cafe Aroma",
        "category": "Dining",
        "amount": 35.00,
        "account": "Visa 1234",
        "currency": "₪",
        "notes": "Lunch with friends",
    },
]

SEED_INCOMES = [
    {
        "date": "2025-11-01",
        "category": "Salary",
        "amount": 8200.00,
        "account": "Bank Leumi",
        "currency": "₪",
        "notes": "November salary",
    },
    {
        "date": "2025-11-10",
        "category": "Freelance",
        "amount": 1250.00,
        "account": "PayPal",
        "currency": "₪",
        "notes": "Client project",
    },
]


def seed_database():
    """Seed the database with sample data."""
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_expenses = db.query(Expense).count()
        existing_incomes = db.query(Income).count()

        if existing_expenses > 0 or existing_incomes > 0:
            print(f"Database already has data (expenses: {existing_expenses}, incomes: {existing_incomes}). Skipping seed.")
            return

        # Insert expenses
        for expense_data in SEED_EXPENSES:
            expense = Expense(**expense_data)
            db.add(expense)

        # Insert incomes
        for income_data in SEED_INCOMES:
            income = Income(**income_data)
            db.add(income)

        db.commit()
        print(f"Seeded {len(SEED_EXPENSES)} expenses and {len(SEED_INCOMES)} incomes.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
