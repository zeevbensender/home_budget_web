from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory store (mock DB)
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
]


class ExpenseCreate(BaseModel):
    date: str
    business: str | None = None
    category: str
    amount: float
    account: str
    currency: str
    notes: str | None = None


@router.get("/expense")
def list_expenses():
    return expenses


@router.post("/expense")
def create_expense(expense: ExpenseCreate):
    new_id = max([e["id"] for e in expenses], default=0) + 1
    data = expense.dict()
    data["id"] = new_id
    expenses.append(data)
    return {"status": "created", "expense": data}
