from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.expense_service import ExpenseService

router = APIRouter()


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


class ExpenseFullUpdate(BaseModel):
    date: Optional[str] = None
    business: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    account: Optional[str] = None
    currency: Optional[str] = None
    notes: Optional[str] = None


@router.get("/expense")
def list_expenses(db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    return expense_service.list_expenses()


@router.post("/expense")
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    data = expense.model_dump()
    created_expense = expense_service.create_expense(data)
    return {"status": "created", "expense": created_expense}


@router.patch("/expense/{expense_id}")
def update_expense(expense_id: int, update: ExpenseUpdate, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    try:
        updated_expense = expense_service.update_expense(
            expense_id, update.field, update.value
        )
        if updated_expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"status": "updated", "expense": updated_expense}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/expense/{expense_id}")
def replace_expense(expense_id: int, expense: ExpenseFullUpdate, db: Session = Depends(get_db)):
    """Full update of an expense (for mobile modal edit)."""
    expense_service = ExpenseService(db)
    
    # Get existing expense
    existing = expense_service.repository.get(expense_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Build update dict with only provided fields
    update_data = expense.model_dump(exclude_unset=True)
    
    # Convert to database format
    db_update_data = expense_service._convert_to_db_format(update_data)
    
    # Update in database
    try:
        updated = expense_service.repository.update(expense_id, db_update_data)
        if not updated:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Convert and return
        result = expense_service._convert_from_db_format(updated)
        return {"status": "updated", "expense": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/expense/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    deleted = expense_service.delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "deleted", "id": expense_id}


class BulkDeleteRequest(BaseModel):
    ids: list[int]


@router.post("/expense/bulk-delete")
def bulk_delete_expense(req: BulkDeleteRequest, db: Session = Depends(get_db)):
    expense_service = ExpenseService(db)
    deleted_count = expense_service.bulk_delete_expenses(req.ids)
    return {"status": "deleted", "count": deleted_count}
