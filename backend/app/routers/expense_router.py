from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.storage_factory import get_expense_repository

router = APIRouter()


class ExpenseCreate(BaseModel):
    date: str
    business: Optional[str] = None
    category: str
    amount: float
    account: str
    currency: Optional[str] = None
    notes: Optional[str] = None


class ExpenseUpdate(BaseModel):
    field: str
    value: str | float | None


class BulkDeleteRequest(BaseModel):
    ids: list[int]


@router.get("/expense")
def list_expenses():
    repo = get_expense_repository()
    return repo.list_all()


@router.post("/expense")
def create_expense(expense: ExpenseCreate):
    repo = get_expense_repository()
    data = expense.model_dump()
    result = repo.create(data)
    return {"status": "created", "expense": result}


@router.patch("/expense/{expense_id}")
def update_expense(expense_id: int, update: ExpenseUpdate):
    repo = get_expense_repository()
    result = repo.update(expense_id, update.field, update.value)
    if result is None:
        # Check if the expense exists to give appropriate error
        expenses = repo.list_all()
        if not any(e["id"] == expense_id for e in expenses):
            raise HTTPException(status_code=404, detail="Expense not found")
        raise HTTPException(status_code=400, detail="Invalid field")
    return {"status": "updated", "expense": result}


@router.delete("/expense/{expense_id}")
def delete_expense(expense_id: int):
    repo = get_expense_repository()
    if repo.delete(expense_id):
        return {"status": "deleted", "id": expense_id}
    raise HTTPException(status_code=404, detail="Expense not found")


@router.post("/expense/bulk-delete")
def bulk_delete_expense(req: BulkDeleteRequest):
    repo = get_expense_repository()
    deleted_count = repo.bulk_delete(req.ids)
    return {"status": "deleted", "count": deleted_count}
