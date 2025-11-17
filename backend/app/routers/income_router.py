from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.storage import load_json, save_json
from app.core.settings import get_default_currency

router = APIRouter()

# Load from JSON or fallback demo data
incomes = load_json("incomes.json", [
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
])

class IncomeCreate(BaseModel):
    date: str
    category: str
    amount: float
    account: str
    currency: Optional[str] = None   # <-- changed
    notes: Optional[str] = None

class IncomeUpdate(BaseModel):
    field: str
    value: str | float | None

@router.get("/income")
def list_incomes():
    return incomes

@router.post("/income")
def create_income(income: IncomeCreate):
    new_id = max([i["id"] for i in incomes], default=0) + 1
    data = income.dict()

    # Auto-fill currency if missing
    if not data.get("currency"):
        data["currency"] = get_default_currency()

    data["id"] = new_id
    incomes.append(data)
    save_json("incomes.json", incomes)
    return {"status": "created", "income": data}

@router.patch("/income/{income_id}")
def update_income(income_id: int, update: IncomeUpdate):
    for inc in incomes:
        if inc["id"] == income_id:
            if update.field not in inc:
                raise HTTPException(status_code=400, detail="Invalid field")

            if update.field == "currency" and update.value is None:
                inc["currency"] = get_default_currency()
            else:
                inc[update.field] = update.value

            save_json("incomes.json", incomes)
            return {"status": "updated", "income": inc}
    raise HTTPException(status_code=404, detail="Income not found")

@router.delete("/income/{income_id}")
def delete_income(income_id: int):
    global incomes
    for inc in incomes:
        if inc["id"] == income_id:
            incomes = [i for i in incomes if i["id"] != income_id]
            save_json("incomes.json", incomes)
            return {"status": "deleted", "id": income_id}
    raise HTTPException(status_code=404, detail="Income not found")

class BulkDeleteRequest(BaseModel):
    ids: list[int]

@router.post("/income/bulk-delete")
def bulk_delete_income(req: BulkDeleteRequest):
    global incomes
    before = len(incomes)

    incomes = [i for i in incomes if i["id"] not in req.ids]

    deleted_count = before - len(incomes)

    save_json("incomes.json", incomes)
    return {"status": "deleted", "count": deleted_count}
