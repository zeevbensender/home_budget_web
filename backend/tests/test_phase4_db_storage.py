"""Tests for Phase 4: Read from Database with USE_DATABASE_STORAGE flag."""

import os
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.models.expense import Expense
from app.models.income import Income
from app.services.expense_service import ExpenseService
from app.services.income_service import IncomeService


class TestExpenseServicePhase4:
    """Tests for ExpenseService with USE_DATABASE_STORAGE feature flag."""

    def setup_method(self):
        """Set up test fixtures."""
        # Clear environment variables
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def teardown_method(self):
        """Clean up after tests."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def test_list_expenses_from_json_when_flag_disabled(self):
        """Should read from JSON when USE_DATABASE_STORAGE is disabled."""
        # Mock repository
        mock_repo = MagicMock()
        mock_db = MagicMock()
        
        service = ExpenseService(mock_db)
        service.repository = mock_repo
        
        # Mock JSON data
        json_data = [
            {"id": 1, "date": "2025-01-01", "category": "Food", "amount": 100, 
             "account": "Cash", "currency": "₪", "business": None, "notes": None}
        ]
        with patch.object(service, '_load_expenses', return_value=json_data):
            result = service.list_expenses()
        
        # Should return JSON data
        assert result == json_data
        # Should not call repository
        mock_repo.list.assert_not_called()

    def test_list_expenses_from_db_when_flag_enabled(self):
        """Should read from database when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true"}):
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
            assert result[0]["date"] == "2025-01-01"
            assert result[0]["category"] == "Food"
            assert result[0]["amount"] == 100.0
            assert result[0]["currency"] == "₪"

    def test_get_expense_from_db_when_flag_enabled(self):
        """Should read single expense from database when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true"}):
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
            mock_repo.get.return_value = mock_expense
            mock_db = MagicMock()
            
            service = ExpenseService(mock_db)
            service.repository = mock_repo
            
            result = service.get_expense(1)
            
            # Should call repository
            mock_repo.get.assert_called_once_with(1)
            
            # Should return dictionary format
            assert result["id"] == 1
            assert result["date"] == "2025-01-01"
            assert result["amount"] == 100.0

    def test_create_expense_writes_to_db_when_flag_enabled(self):
        """Should write to database first when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true", "FF_DUAL_WRITE_ENABLED": "true"}):
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
            
            # Mock JSON operations for dual-write
            with patch.object(service, '_load_expenses', return_value=[]):
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
            
            # Should also dual-write to JSON
            mock_save.assert_called_once()
            
            # Should return dictionary format
            assert result["id"] == 1
            assert result["amount"] == 100.0

    def test_update_expense_updates_db_when_flag_enabled(self):
        """Should update database first when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true", "FF_DUAL_WRITE_ENABLED": "true"}):
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
            
            # Mock JSON operations for dual-write
            json_data = [{"id": 1, "date": "2025-01-01", "category": "Food", "amount": 100.0, 
                         "account": "Cash", "currency": "₪", "business": None, "notes": None}]
            with patch.object(service, '_load_expenses', return_value=json_data):
                with patch.object(service, '_save_expenses') as mock_save:
                    result = service.update_expense(1, "amount", 150.0)
            
            # Should call repository to update in DB
            mock_repo.update.assert_called_once()
            
            # Should also dual-write to JSON
            mock_save.assert_called_once()
            
            # Should return updated data
            assert result["amount"] == 150.0

    def test_delete_expense_deletes_from_db_when_flag_enabled(self):
        """Should delete from database first when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true", "FF_DUAL_WRITE_ENABLED": "true"}):
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
            
            # Mock JSON operations for dual-write
            json_data = [{"id": 1, "date": "2025-01-01", "category": "Food", "amount": 100.0,
                         "account": "Cash", "currency": "₪", "business": None, "notes": None}]
            with patch.object(service, '_load_expenses', return_value=json_data):
                with patch.object(service, '_save_expenses') as mock_save:
                    result = service.delete_expense(1)
            
            # Should call repository to delete from DB
            mock_repo.delete.assert_called_once_with(1)
            
            # Should also dual-write to JSON
            mock_save.assert_called_once()
            
            # Should return success
            assert result is True

    def test_fallback_to_json_when_no_repository(self):
        """Should fallback to JSON when repository is not available."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true"}):
            # Create service without repository
            service = ExpenseService(db=None)
            
            # Mock JSON data
            json_data = [{"id": 1, "date": "2025-01-01", "category": "Food", "amount": 100.0,
                         "account": "Cash", "currency": "₪", "business": None, "notes": None}]
            with patch.object(service, '_load_expenses', return_value=json_data):
                result = service.list_expenses()
            
            # Should return JSON data as fallback
            assert result == json_data


class TestIncomeServicePhase4:
    """Tests for IncomeService with USE_DATABASE_STORAGE feature flag."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def teardown_method(self):
        """Clean up after tests."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def test_list_incomes_from_db_when_flag_enabled(self):
        """Should read from database when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true"}):
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

    def test_create_income_writes_to_db_when_flag_enabled(self):
        """Should write to database first when USE_DATABASE_STORAGE is enabled."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true", "FF_DUAL_WRITE_ENABLED": "true"}):
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
            
            # Mock JSON operations for dual-write
            with patch.object(service, '_load_incomes', return_value=[]):
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
            
            # Should also dual-write to JSON
            mock_save.assert_called_once()
            
            # Should return dictionary format
            assert result["id"] == 1
            assert result["amount"] == 5000.0


class TestDualWritePhase4:
    """Tests for dual-write behavior in Phase 4."""

    def setup_method(self):
        """Set up test fixtures."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def teardown_method(self):
        """Clean up after tests."""
        os.environ.pop("FF_USE_DATABASE_STORAGE", None)
        os.environ.pop("FF_DUAL_WRITE_ENABLED", None)

    def test_dual_write_disabled_no_json_write(self):
        """Should not write to JSON when dual-write is disabled in Phase 4."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true", "FF_DUAL_WRITE_ENABLED": "false"}):
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
            with patch.object(service, '_load_expenses', return_value=[]):
                with patch.object(service, '_save_expenses') as mock_save:
                    data = {
                        "date": "2025-01-01",
                        "category": "Food",
                        "amount": 100.0,
                        "account": "Cash",
                        "currency": "₪"
                    }
                    service.create_expense(data)
            
            # Should NOT write to JSON
            mock_save.assert_not_called()

    def test_dual_write_handles_json_errors_gracefully(self):
        """Should handle JSON write errors gracefully in Phase 4 dual-write."""
        with patch.dict(os.environ, {"FF_USE_DATABASE_STORAGE": "true", "FF_DUAL_WRITE_ENABLED": "true"}):
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
            
            # Mock JSON operations to raise error
            with patch.object(service, '_load_expenses', return_value=[]):
                with patch.object(service, '_save_expenses', side_effect=Exception("JSON error")):
                    data = {
                        "date": "2025-01-01",
                        "category": "Food",
                        "amount": 100.0,
                        "account": "Cash",
                        "currency": "₪"
                    }
                    # Should not raise exception despite JSON error
                    result = service.create_expense(data)
            
            # Should still return result from DB
            assert result["id"] == 1
