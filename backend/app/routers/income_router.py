from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.storage import load_json, save_json

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
    currency: str
    notes: str | None = None

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
            inc[update.field] = update.value
            save_json("incomes.json", incomes)
            return {"status": "updated", "income": inc}
    raise HTTPException(status_code=404, detail="Income not found")
