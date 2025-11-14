from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory store (mock DB)
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


class IncomeCreate(BaseModel):
    date: str
    category: str
    amount: float
    account: str
    currency: str
    notes: str | None = None


@router.get("/income")
def list_incomes():
    return incomes


@router.post("/income")
def create_income(income: IncomeCreate):
    new_id = max([i["id"] for i in incomes], default=0) + 1
    data = income.dict()
    data["id"] = new_id
    incomes.append(data)
    return {"status": "created", "income": data}
