from sqlalchemy import Column, Integer, String, Float, Date
from app.db.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    business = Column(String, nullable=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="₪")
    notes = Column(String, nullable=True)


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    currency = Column(String, nullable=False, default="₪")
    notes = Column(String, nullable=True)
