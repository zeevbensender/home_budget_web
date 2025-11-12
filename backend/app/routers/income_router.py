from fastapi import APIRouter

router = APIRouter()

@router.get("/income")
def get_incomes():
    return [
        {"id": 1, "source": "Salary", "amount": 3200.00, "date": "2025-11-01"},
        {"id": 2, "source": "Freelance", "amount": 750.00, "date": "2025-11-10"},
    ]
