from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Mock DB (temporary)
incomes = [
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

@router.get("/income")
def get_incomes():
    return incomes


# ---- new part ----
class IncomeUpdate(BaseModel):
    field: str
    value: str | float | None = None


@router.patch("/income/{income_id}")
def update_income(income_id: int, update: IncomeUpdate):
    print("INSIDE INC")
    for inc in incomes:
        if inc["id"] == income_id:
            inc[update.field] = update.value
            return {"status": "updated", "income": inc}
    raise HTTPException(status_code=404, detail="Income not found")
