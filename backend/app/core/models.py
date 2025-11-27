"""SQLAlchemy ORM models for Home Budget Web."""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Expense(Base):
    """Expense model representing expenses in the database."""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    business = Column(String, nullable=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "business": self.business,
            "category": self.category,
            "amount": self.amount,
            "account": self.account,
            "currency": self.currency,
            "notes": self.notes,
        }


class Income(Base):
    """Income model representing incomes in the database."""

    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    notes = Column(String, nullable=True)

    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "category": self.category,
            "amount": self.amount,
            "account": self.account,
            "currency": self.currency,
            "notes": self.notes,
        }
