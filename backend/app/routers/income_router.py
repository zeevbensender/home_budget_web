from fastapi import APIRouter
from typing import List

router = APIRouter()

# Example mock data (will be replaced later)
_mock_incomes = [
    {"id": 1, "amount": 5000.0, "source": "Salary"},
    {"id": 2, "amount": 250.0, "source": "Freelance"},
]

@router.get("/", tags=["Incomes"])
def list_incomes() -> List[dict]:
    """Temporary endpoint — returns mock income data."""
    return _mock_incomes

@router.post("/", tags=["Incomes"])
def add_income(income: dict) -> dict:
    """Temporary endpoint — accepts any JSON object."""
    income["id"] = len(_mock_incomes) + 1
    _mock_incomes.append(income)
    return {"message": "Income added", "income": income}
