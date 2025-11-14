from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.storage import load_json, save_json

router = APIRouter()

# Load from JSON or fallback demo data
expenses = load_json("expenses.json", [
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
])

class ExpenseCreate(BaseModel):
    date: str
    business: str | None = None
    category: str
    amount: float
    account: str
    currency: str
    notes: str | None = None

class ExpenseUpdate(BaseModel):
    field: str
    value: str | float | None

@router.get("/expense")
def list_expenses():
    return expenses

@router.post("/expense")
def create_expense(expense: ExpenseCreate):
    new_id = max([e["id"] for e in expenses], default=0) + 1
    data = expense.dict()
    data["id"] = new_id
    expenses.append(data)
    save_json("expenses.json", expenses)
    return {"status": "created", "expense": data}

@router.patch("/expense/{expense_id}")
def update_expense(expense_id: int, update: ExpenseUpdate):
    for exp in expenses:
        if exp["id"] == expense_id:
            if update.field not in exp:
                raise HTTPException(status_code=400, detail="Invalid field")
            exp[update.field] = update.value
            save_json("expenses.json", expenses)
            return {"status": "updated", "expense": exp}
    raise HTTPException(status_code=404, detail="Expense not found")
