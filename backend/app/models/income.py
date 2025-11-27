"""
Income model - maps the essential JSON fields from the PoC.
"""

from sqlalchemy import Integer, String, Numeric, Date, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Income(Base):
    """
    Income table for tracking individual income entries.
    
    Maps the following JSON fields:
    - id: unique identifier (primary key)
    - date: date of the income
    - category: income category/source
    - amount: income amount
    - account: account receiving the income
    - currency: currency symbol
    - notes: additional notes (optional)
    """
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    account: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
