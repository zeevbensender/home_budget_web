"""Tests for Phase 5: Full Database Mode with dual-write disabled.

Phase 5 tests verify that the system works correctly when:
- USE_DATABASE_STORAGE=true (reads from PostgreSQL)
- DUAL_WRITE_ENABLED=false (writes only to PostgreSQL)

This is the production-ready configuration.
"""

import os
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.models.expense import Expense
from app.models.income import Income
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService


class TestExpenseServicePhase5:
    """Tests for ExpenseService in Phase 5 (full database mode)."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear environment variables
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def teardown_method(self):
        """Clean up after tests."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def test_list_expenses_from_db_only(self):
        """Should read from database only when in Phase 5 mode."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
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

    def test_create_expense_db_only_no_dual_write(self):
        """Should write to database only, not JSON, when dual-write is disabled."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
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
            
            # Mock JSON operations
            with patch.object(service, '_load_expenses', return_value=[]) as mock_load:
                with patch.object(service, '_save_expenses') as mock_save:
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
            
            # Should NOT write to JSON (dual-write disabled)
            mock_save.assert_not_called()
            mock_load.assert_not_called()
            
            # Should return dictionary format
            assert result["id"] == 1
            assert result["amount"] == 100.0

    def test_update_expense_db_only_no_dual_write(self):
        """Should update database only, not JSON, when dual-write is disabled."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
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
            
            # Mock JSON operations
            with patch.object(service, '_load_expenses', return_value=[]) as mock_load:
                with patch.object(service, '_save_expenses') as mock_save:
                    result = service.update_expense(1, "amount", 150.0)
            
            # Should call repository to update in DB
            mock_repo.update.assert_called_once()
            
            # Should NOT write to JSON (dual-write disabled)
            mock_save.assert_not_called()
            mock_load.assert_not_called()
            
            # Should return updated data
            assert result["amount"] == 150.0

    def test_delete_expense_db_only_no_dual_write(self):
        """Should delete from database only, not JSON, when dual-write is disabled."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
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
            
            # Mock JSON operations
            with patch.object(service, '_load_expenses', return_value=[]) as mock_load:
                with patch.object(service, '_save_expenses') as mock_save:
                    result = service.delete_expense(1)
            
            # Should call repository to delete from DB
            mock_repo.delete.assert_called_once_with(1)
            
            # Should NOT write to JSON (dual-write disabled)
            mock_save.assert_not_called()
            mock_load.assert_not_called()
            
            # Should return success
            assert result is True

    def test_bulk_delete_db_only_no_dual_write(self):
        """Should bulk delete from database only, not JSON, when dual-write is disabled."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
            mock_repo = MagicMock()
            mock_repo.bulk_delete.return_value = 3
            mock_db = MagicMock()
            
            service = ExpenseService(mock_db)
            service.repository = mock_repo
            
            # Mock JSON operations
            with patch.object(service, '_load_expenses', return_value=[]) as mock_load:
                with patch.object(service, '_save_expenses') as mock_save:
                    result = service.bulk_delete_expenses([1, 2, 3])
            
            # Should call repository to delete from DB
            mock_repo.bulk_delete.assert_called_once_with([1, 2, 3])
            
            # Should NOT write to JSON (dual-write disabled)
            mock_save.assert_not_called()
            mock_load.assert_not_called()
            
            # Should return count
            assert result == 3


class TestIncomeServicePhase5:
    """Tests for IncomeService in Phase 5 (full database mode)."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def teardown_method(self):
        """Clean up after tests."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def test_create_income_db_only_no_dual_write(self):
        """Should write to database only, not JSON, when dual-write is disabled."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
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
            
            # Mock JSON operations
            with patch.object(service, '_load_incomes', return_value=[]) as mock_load:
                with patch.object(service, '_save_incomes') as mock_save:
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
            
            # Should NOT write to JSON (dual-write disabled)
            mock_save.assert_not_called()
            mock_load.assert_not_called()
            
            # Should return dictionary format
            assert result["id"] == 1
            assert result["amount"] == 5000.0

    def test_list_incomes_from_db_only(self):
        """Should read from database only when in Phase 5 mode."""
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
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


class TestRollbackCapability:
    """Tests for rollback capability in Phase 5."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def teardown_method(self):
        """Clean up after tests."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def test_can_rollback_to_phase4_by_enabling_dual_write(self):
        """Should be able to rollback from Phase 5 to Phase 4 by enabling dual-write."""
        # Start in Phase 5
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
            mock_repo = MagicMock()
            mock_expense = Expense(
                id=1, date=date(2025, 1, 1), category="Food",
                amount=Decimal("100.00"), account="Cash", currency="₪",
                business=None, notes=None
            )
            mock_repo.create.return_value = mock_expense
            mock_db = MagicMock()
            
            service = ExpenseService(mock_db)
            service.repository = mock_repo
            
            with patch.object(service, '_save_expenses') as mock_save:
                service.create_expense({
                    "date": "2025-01-01", "category": "Food",
                    "amount": 100.0, "account": "Cash", "currency": "₪"
                })
            
            # Dual-write should be disabled
            mock_save.assert_not_called()
        
        # Now rollback to Phase 4 by enabling dual-write
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "true"
        }):
            service = ExpenseService(mock_db)
            service.repository = mock_repo
            
            with patch.object(service, '_load_expenses', return_value=[]):
                with patch.object(service, '_save_expenses') as mock_save:
                    service.create_expense({
                        "date": "2025-01-01", "category": "Food",
                        "amount": 100.0, "account": "Cash", "currency": "₪"
                    })
            
            # Dual-write should now be enabled
            mock_save.assert_called_once()

    def test_can_rollback_to_json_by_disabling_use_database_storage(self):
        """Should be able to rollback to JSON mode by disabling USE_DATABASE_STORAGE."""
        # Start in Phase 5
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "true",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
            mock_repo = MagicMock()
            mock_db = MagicMock()
            service = ExpenseService(mock_db)
            service.repository = mock_repo
            
            mock_expense = Expense(
                id=1, date=date(2025, 1, 1), category="Food",
                amount=Decimal("100.00"), account="Cash", currency="₪",
                business=None, notes=None
            )
            mock_repo.list.return_value = [mock_expense]
            
            result = service.list_expenses()
            
            # Should read from database
            mock_repo.list.assert_called_once()
        
        # Now rollback to JSON mode
        with patch.dict(os.environ, {
            "FF_USE_DATABASE_STORAGE": "false",
            "FF_DUAL_WRITE_ENABLED": "false"
        }):
            service = ExpenseService(mock_db)
            service.repository = mock_repo
            mock_repo.list.reset_mock()
            
            json_data = [{"id": 1, "date": "2025-01-01", "category": "Food",
                         "amount": 100.0, "account": "Cash", "currency": "₪",
                         "business": None, "notes": None}]
            
            with patch.object(service, '_load_expenses', return_value=json_data):
                result = service.list_expenses()
            
            # Should read from JSON
            mock_repo.list.assert_not_called()
            assert result == json_data
