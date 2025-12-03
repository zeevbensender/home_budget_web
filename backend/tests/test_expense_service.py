"""Tests for the expense service with feature flags."""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.expense_service import (format_expense_amount,
                                          get_expense_summary)


class TestFormatExpenseAmount:
    """Tests for format_expense_amount with feature flags."""

    def test_default_format_v1(self):
        """Should use simple format when flag is disabled."""
        os.environ.pop("FF_EXPENSE_AMOUNT_V2_FORMAT", None)
        result = format_expense_amount(1234.50, "₪")
        assert result == "1234.50 ₪"

    def test_format_v2_enabled(self):
        """Should use thousand separator format when flag is enabled."""
        with patch.dict(os.environ, {"FF_EXPENSE_AMOUNT_V2_FORMAT": "true"}):
            result = format_expense_amount(1234.50, "₪")
            assert result == "1,234.50 ₪"

    def test_format_v2_large_number(self):
        """Should format large numbers correctly with v2."""
        with patch.dict(os.environ, {"FF_EXPENSE_AMOUNT_V2_FORMAT": "true"}):
            result = format_expense_amount(1234567.89, "$")
            assert result == "1,234,567.89 $"


class TestGetExpenseSummary:
    """Tests for get_expense_summary with feature flags."""

    def test_basic_summary_when_flag_disabled(self):
        """Should return basic summary when flag is disabled."""
        os.environ.pop("FF_ENHANCED_EXPENSE_STATS", None)
        expenses = [
            {"amount": 100},
            {"amount": 200},
            {"amount": 300},
        ]
        result = get_expense_summary(expenses)
        assert result == {"total": 600, "count": 3}
        assert "average" not in result
        assert "min" not in result
        assert "max" not in result

    def test_enhanced_summary_when_flag_enabled(self):
        """Should return enhanced summary when flag is enabled."""
        with patch.dict(os.environ, {"FF_ENHANCED_EXPENSE_STATS": "true"}):
            expenses = [
                {"amount": 100},
                {"amount": 200},
                {"amount": 300},
            ]
            result = get_expense_summary(expenses)
            assert result["total"] == 600
            assert result["count"] == 3
            assert result["average"] == 200
            assert result["min"] == 100
            assert result["max"] == 300

    def test_empty_expenses(self):
        """Should handle empty expenses list."""
        result = get_expense_summary([])
        assert result == {"total": 0, "count": 0}
