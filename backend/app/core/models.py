"""SQLAlchemy models for PoC entities.

This module defines the database models for Expense and Income entities
using SQLAlchemy 2.0 declarative syntax.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


class Expense(Base):
    """Expense model representing an expense transaction."""

    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    business: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    account: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="₪")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "business": self.business,
            "category": self.category,
            "amount": float(self.amount) if self.amount else None,
            "account": self.account,
            "currency": self.currency,
            "notes": self.notes,
        }


class Income(Base):
    """Income model representing an income transaction."""

    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    account: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="₪")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "category": self.category,
            "amount": float(self.amount) if self.amount else None,
            "account": self.account,
            "currency": self.currency,
            "notes": self.notes,
        }
