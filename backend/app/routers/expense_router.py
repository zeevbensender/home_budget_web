from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.storage import load_json, save_json
from app.core.settings import get_default_currency

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
    business: Optional[str] = None
    category: str
    amount: float
    account: str
    currency: Optional[str] = None  # <-- changed
    notes: Optional[str] = None

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

    # Auto-fill currency if missing
    if not data.get("currency"):
        data["currency"] = get_default_currency()

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

            # Allow updating to null (keep old), but fallback if needed
            if update.field == "currency" and update.value is None:
                exp["currency"] = get_default_currency()
            else:
                exp[update.field] = update.value

            save_json("expenses.json", expenses)
            return {"status": "updated", "expense": exp}

    raise HTTPException(status_code=404, detail="Expense not found")

@router.delete("/expense/{expense_id}")
def delete_expense(expense_id: int):
    global expenses
    for exp in expenses:
        if exp["id"] == expense_id:
            expenses = [e for e in expenses if e["id"] != expense_id]
            save_json("expenses.json", expenses)
            return {"status": "deleted", "id": expense_id}
    raise HTTPException(status_code=404, detail="Expense not found")

class BulkDeleteRequest(BaseModel):
    ids: list[int]

@router.post("/expense/bulk-delete")
def bulk_delete_expense(req: BulkDeleteRequest):
    global expenses
    before = len(expenses)

    expenses = [e for e in expenses if e["id"] not in req.ids]

    deleted_count = before - len(expenses)

    save_json("expenses.json", expenses)
    return {"status": "deleted", "count": deleted_count}
