from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Mock DB (temporary)
expenses = [
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

@router.get("/expense")
def get_expenses():
    return expenses


# ---- new part ----
class ExpenseUpdate(BaseModel):
    field: str
    value: str | float | None = None


@router.patch("/expense/{expense_id}")
def update_expense(expense_id: int, update: ExpenseUpdate):
    print("INSIDE EXP")
    for exp in expenses:
        if exp["id"] == expense_id:
            exp[update.field] = update.value
            return {"status": "updated", "expense": exp}
    raise HTTPException(status_code=404, detail="Expense not found")
