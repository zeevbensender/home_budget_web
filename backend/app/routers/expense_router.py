from fastapi import APIRouter
from typing import List

router = APIRouter()

# Example mock data (will be replaced later)
_mock_expenses = [
    {"id": 1, "amount": 25.5, "category": "Food", "business": "Coffee Shop"},
    {"id": 2, "amount": 120.0, "category": "Utilities", "business": "Electric Co."},
]

@router.get("/", tags=["Expenses"])
def list_expenses() -> List[dict]:
    """Temporary endpoint — returns mock expense data."""
    return _mock_expenses

@router.post("/", tags=["Expenses"])
def add_expense(expense: dict) -> dict:
    """Temporary endpoint — accepts any JSON object."""
    expense["id"] = len(_mock_expenses) + 1
    _mock_expenses.append(expense)
    return {"message": "Expense added", "expense": expense}
