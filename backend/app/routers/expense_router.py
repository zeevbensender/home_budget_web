from fastapi import APIRouter

router = APIRouter()

@router.get("/expense")
def get_expenses():
    return [
        {
            "id": 1,
            "date": "2025-11-01",
            "business": "SuperSal",
            "category": "Groceries",
            "amount": 142.50,
            "account": "Visa 1234",
            "currency": "₪",
            "notes": "Weekly shopping",
        },
        {
            "id": 2,
            "date": "2025-11-05",
            "business": "Rav-Kav",
            "category": "Transport",
            "amount": 15.00,
            "account": "Cash",
            "currency": "₪",
            "notes": "Bus to work",
        },
        {
            "id": 3,
            "date": "2025-11-08",
            "business": "IEC",
            "category": "Utilities",
            "amount": 320.30,
            "account": "Direct debit",
            "currency": "₪",
            "notes": "Electricity bill",
        },
    ]
