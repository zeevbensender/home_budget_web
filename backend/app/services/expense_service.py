"""
Expense service with feature flag examples.

This module demonstrates how to use feature flags in the service layer
to enable phased rollouts of new functionality.
"""

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.feature_flags import is_feature_enabled


def format_expense_amount(
    amount: float,
    currency: str,
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> str:
    """
    Format expense amount with currency symbol.

    This demonstrates feature flag usage for a phased rollout of
    a new formatting style.

    Feature flag: EXPENSE_AMOUNT_V2_FORMAT
    - When disabled (default): Returns simple format "142.50 ₪"
    - When enabled: Returns formatted with thousand separators "1,234.50 ₪"

    Args:
        amount: The expense amount
        currency: The currency symbol
        user_id: Optional user ID for per-user flag checks
        db: Optional database session for DB-based flags

    Returns:
        Formatted amount string
    """
    if is_feature_enabled("EXPENSE_AMOUNT_V2_FORMAT", user_id=user_id, db=db):
        # New format with thousand separators (v2)
        return f"{amount:,.2f} {currency}"
    else:
        # Original format (v1)
        return f"{amount:.2f} {currency}"


def get_expense_summary(
    expenses: list[dict[str, Any]],
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    """
    Get expense summary with optional enhanced statistics.

    Feature flag: ENHANCED_EXPENSE_STATS
    - When disabled (default): Returns basic summary (total, count)
    - When enabled: Returns enhanced summary (total, count, average, min, max)

    Args:
        expenses: List of expense dictionaries
        user_id: Optional user ID for per-user flag checks
        db: Optional database session for DB-based flags

    Returns:
        Summary dictionary
    """
    if not expenses:
        return {"total": 0, "count": 0}

    amounts = [e.get("amount", 0) for e in expenses]
    total = sum(amounts)
    count = len(amounts)

    summary: dict[str, Any] = {
        "total": round(total, 2),
        "count": count,
    }

    # Enhanced statistics when feature flag is enabled
    if is_feature_enabled("ENHANCED_EXPENSE_STATS", user_id=user_id, db=db):
        summary["average"] = round(total / count, 2) if count > 0 else 0
        summary["min"] = round(min(amounts), 2) if amounts else 0
        summary["max"] = round(max(amounts), 2) if amounts else 0

    return summary
