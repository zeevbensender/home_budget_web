from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.expense_service import ExpenseService

router = APIRouter()

# Initialize service (uses JSON storage)
expense_service = ExpenseService()


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
    return expense_service.list_expenses()


@router.post("/expense")
def create_expense(expense: ExpenseCreate):
    data = expense.model_dump()
    created_expense = expense_service.create_expense(data)
    return {"status": "created", "expense": created_expense}


@router.patch("/expense/{expense_id}")
def update_expense(expense_id: int, update: ExpenseUpdate):
    try:
        updated_expense = expense_service.update_expense(
            expense_id, update.field, update.value
        )
        if updated_expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"status": "updated", "expense": updated_expense}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/expense/{expense_id}")
def delete_expense(expense_id: int):
    deleted = expense_service.delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "deleted", "id": expense_id}


class BulkDeleteRequest(BaseModel):
    ids: list[int]


@router.post("/expense/bulk-delete")
def bulk_delete_expense(req: BulkDeleteRequest):
    deleted_count = expense_service.bulk_delete_expenses(req.ids)
    return {"status": "deleted", "count": deleted_count}
