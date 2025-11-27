from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base


class Expense(Base):
    """SQLAlchemy model for expenses.

    Note: The date field is stored as a String to match the existing API contract
    which accepts/returns date strings in "YYYY-MM-DD" format.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)  # ISO format string "YYYY-MM-DD"
    business = Column(String, nullable=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="₪")
    notes = Column(String, nullable=True)


class Income(Base):
    """SQLAlchemy model for incomes.

    Note: The date field is stored as a String to match the existing API contract
    which accepts/returns date strings in "YYYY-MM-DD" format.
    """
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)  # ISO format string "YYYY-MM-DD"
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="₪")
    notes = Column(String, nullable=True)
