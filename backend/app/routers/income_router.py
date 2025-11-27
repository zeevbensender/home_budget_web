from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.storage_factory import get_income_repository

router = APIRouter()


class IncomeCreate(BaseModel):
    date: str
    category: str
    amount: float
    account: str
    currency: Optional[str] = None
    notes: Optional[str] = None


class IncomeUpdate(BaseModel):
    field: str
    value: str | float | None


class BulkDeleteRequest(BaseModel):
    ids: list[int]


@router.get("/income")
def list_incomes():
    repo = get_income_repository()
    return repo.list_all()


@router.post("/income")
def create_income(income: IncomeCreate):
    repo = get_income_repository()
    data = income.model_dump()
    result = repo.create(data)
    return {"status": "created", "income": result}


@router.patch("/income/{income_id}")
def update_income(income_id: int, update: IncomeUpdate):
    repo = get_income_repository()
    result = repo.update(income_id, update.field, update.value)
    if result is None:
        # Check if the income exists to give appropriate error
        incomes = repo.list_all()
        if not any(i["id"] == income_id for i in incomes):
            raise HTTPException(status_code=404, detail="Income not found")
        raise HTTPException(status_code=400, detail="Invalid field")
    return {"status": "updated", "income": result}


@router.delete("/income/{income_id}")
def delete_income(income_id: int):
    repo = get_income_repository()
    if repo.delete(income_id):
        return {"status": "deleted", "id": income_id}
    raise HTTPException(status_code=404, detail="Income not found")


@router.post("/income/bulk-delete")
def bulk_delete_income(req: BulkDeleteRequest):
    repo = get_income_repository()
    deleted_count = repo.bulk_delete(req.ids)
    return {"status": "deleted", "count": deleted_count}
