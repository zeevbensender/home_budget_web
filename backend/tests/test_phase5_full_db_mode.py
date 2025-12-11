"""Tests for Phase 5: Full Database Mode with dual-write disabled.

Phase 5 tests verify that the system works correctly when:
- All reads and writes use PostgreSQL
- JSON storage code has been removed

This is the production-ready configuration.
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from app.models.expense import Expense
from app.models.income import Income
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService


class TestExpenseServicePhase5:
    """Tests for ExpenseService in Phase 5 (full database mode)."""

    def test_list_expenses_from_db_only(self):
        """Should read from database only in Phase 5 mode."""
        # Mock repository with SQLAlchemy model instances
        mock_expense = Expense(
            id=1,
            date=date(2025, 1, 1),
            category="Food",
            amount=Decimal("100.00"),
            account="Cash",
            currency="₪",
            business=None,
            notes=None
        )
        
        mock_repo = MagicMock()
        mock_repo.list.return_value = [mock_expense]
        mock_db = MagicMock()
        
        service = ExpenseService(mock_db)
        service.repository = mock_repo
        
        result = service.list_expenses()
        
        # Should call repository
        mock_repo.list.assert_called_once_with(order_by="-date")
        
        # Should return dictionary format
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["amount"] == 100.0

    def test_create_expense_db_only(self):
        """Should write to database only in Phase 5."""
        # Mock repository
        mock_expense = Expense(
            id=1,
            date=date(2025, 1, 1),
            category="Food",
            amount=Decimal("100.00"),
            account="Cash",
            currency="₪",
            business=None,
            notes=None
        )
        
        mock_repo = MagicMock()
        mock_repo.create.return_value = mock_expense
        mock_db = MagicMock()
        
        service = ExpenseService(mock_db)
        service.repository = mock_repo
        
        data = {
            "date": "2025-01-01",
            "category": "Food",
            "amount": 100.0,
            "account": "Cash",
            "currency": "₪"
        }
        result = service.create_expense(data)
        
        # Should call repository to create in DB
        mock_repo.create.assert_called_once()
        
        # Should return dictionary format
        assert result["id"] == 1
        assert result["amount"] == 100.0

    def test_update_expense_db_only(self):
        """Should update database only in Phase 5."""
        # Mock existing and updated expense
        existing_expense = Expense(
            id=1,
            date=date(2025, 1, 1),
            category="Food",
            amount=Decimal("100.00"),
            account="Cash",
            currency="₪",
            business=None,
            notes=None
        )
        
        updated_expense = Expense(
            id=1,
            date=date(2025, 1, 1),
            category="Food",
            amount=Decimal("150.00"),
            account="Cash",
            currency="₪",
            business=None,
            notes=None
        )
        
        mock_repo = MagicMock()
        mock_repo.get.return_value = existing_expense
        mock_repo.update.return_value = updated_expense
        mock_db = MagicMock()
        
        service = ExpenseService(mock_db)
        service.repository = mock_repo
        
        result = service.update_expense(1, "amount", 150.0)
        
        # Should call repository to update in DB
        mock_repo.update.assert_called_once()
        
        # Should return updated data
        assert result["amount"] == 150.0

    def test_delete_expense_db_only(self):
        """Should delete from database only in Phase 5."""
        # Mock existing expense
        existing_expense = Expense(
            id=1,
            date=date(2025, 1, 1),
            category="Food",
            amount=Decimal("100.00"),
            account="Cash",
            currency="₪",
            business=None,
            notes=None
        )
        
        mock_repo = MagicMock()
        mock_repo.get.return_value = existing_expense
        mock_repo.delete.return_value = True
        mock_db = MagicMock()
        
        service = ExpenseService(mock_db)
        service.repository = mock_repo
        
        result = service.delete_expense(1)
        
        # Should call repository to delete from DB
        mock_repo.delete.assert_called_once_with(1)
        
        # Should return success
        assert result is True

    def test_bulk_delete_db_only(self):
        """Should bulk delete from database only in Phase 5."""
        mock_repo = MagicMock()
        mock_repo.bulk_delete.return_value = 3
        mock_db = MagicMock()
        
        service = ExpenseService(mock_db)
        service.repository = mock_repo
        
        result = service.bulk_delete_expenses([1, 2, 3])
        
        # Should call repository to delete from DB
        mock_repo.bulk_delete.assert_called_once_with([1, 2, 3])
        
        # Should return count
        assert result == 3


class TestIncomeServicePhase5:
    """Tests for IncomeService in Phase 5 (full database mode)."""

    def test_create_income_db_only(self):
        """Should write to database only in Phase 5."""
        # Mock repository
        mock_income = Income(
            id=1,
            date=date(2025, 1, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
            notes=None
        )
        
        mock_repo = MagicMock()
        mock_repo.create.return_value = mock_income
        mock_db = MagicMock()
        
        service = IncomeService(mock_db)
        service.repository = mock_repo
        
        data = {
            "date": "2025-01-01",
            "category": "Salary",
            "amount": 5000.0,
            "account": "Bank",
            "currency": "₪"
        }
        result = service.create_income(data)
        
        # Should call repository to create in DB
        mock_repo.create.assert_called_once()
        
        # Should return dictionary format
        assert result["id"] == 1
        assert result["amount"] == 5000.0

    def test_list_incomes_from_db_only(self):
        """Should read from database only in Phase 5 mode."""
        # Mock repository
        mock_income = Income(
            id=1,
            date=date(2025, 1, 1),
            category="Salary",
            amount=Decimal("5000.00"),
            account="Bank",
            currency="₪",
            notes=None
        )
        
        mock_repo = MagicMock()
        mock_repo.list.return_value = [mock_income]
        mock_db = MagicMock()
        
        service = IncomeService(mock_db)
        service.repository = mock_repo
        
        result = service.list_incomes()
        
        # Should call repository
        mock_repo.list.assert_called_once_with(order_by="-date")
        
        # Should return dictionary format
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["amount"] == 5000.0

