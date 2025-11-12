from fastapi import APIRouter

router = APIRouter()

@router.get("/expense")
def get_expenses():
    return [
        {"id": 1, "category": "Food", "amount": 42.50, "date": "2025-11-01"},
        {"id": 2, "category": "Transport", "amount": 15.00, "date": "2025-11-05"},
        {"id": 3, "category": "Utilities", "amount": 120.30, "date": "2025-11-08"},
    ]
