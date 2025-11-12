from fastapi import APIRouter

router = APIRouter()

@router.get("/income")
def get_incomes():
    return [
        {
            "id": 1,
            "date": "2025-11-01",
            "category": "Salary",
            "amount": 8200.00,
            "account": "Bank Leumi",
            "currency": "₪",
            "notes": "November salary",
        },
        {
            "id": 2,
            "date": "2025-11-10",
            "category": "Freelance",
            "amount": 1250.00,
            "account": "PayPal",
            "currency": "₪",
            "notes": "Client project",
        },
    ]
