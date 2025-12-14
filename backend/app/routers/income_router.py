from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.income_service import IncomeService

router = APIRouter()


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
def list_incomes(db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    return income_service.list_incomes()


@router.post("/income")
def create_income(income: IncomeCreate, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    data = income.model_dump()
    created_income = income_service.create_income(data)
    return {"status": "created", "income": created_income}


@router.patch("/income/{income_id}")
def update_income(income_id: int, update: IncomeUpdate, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    try:
        updated_income = income_service.update_income(
            income_id, update.field, update.value
        )
        if updated_income is None:
            raise HTTPException(status_code=404, detail="Income not found")
        return {"status": "updated", "income": updated_income}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/income/{income_id}")
def delete_income(income_id: int, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    deleted = income_service.delete_income(income_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"status": "deleted", "id": income_id}


class BulkDeleteRequest(BaseModel):
    ids: list[int]


@router.post("/income/bulk-delete")
def bulk_delete_income(req: BulkDeleteRequest, db: Session = Depends(get_db)):
    income_service = IncomeService(db)
    deleted_count = income_service.bulk_delete_incomes(req.ids)
    return {"status": "deleted", "count": deleted_count}
