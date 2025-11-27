"""Repository layer for expense operations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.core.settings import get_default_currency


class ExpenseRepositoryInterface(ABC):
    """Abstract interface for expense repository."""

    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all expenses."""
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new expense."""
        pass

    @abstractmethod
    def update(self, expense_id: int, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Update an expense field."""
        pass

    @abstractmethod
    def delete(self, expense_id: int) -> bool:
        """Delete an expense."""
        pass

    @abstractmethod
    def bulk_delete(self, ids: List[int]) -> int:
        """Bulk delete expenses. Returns the count of deleted items."""
        pass


class JsonExpenseRepository(ExpenseRepositoryInterface):
    """JSON-based expense repository."""

    def __init__(self, storage_module):
        from app.core.storage import load_json, save_json
        self._load_json = load_json
        self._save_json = save_json
        self._expenses = load_json("expenses.json", [
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

    def list_all(self) -> List[Dict[str, Any]]:
        return self._expenses

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = max([e["id"] for e in self._expenses], default=0) + 1
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        data["id"] = new_id
        self._expenses.append(data)
        self._save_json("expenses.json", self._expenses)
        return data

    def update(self, expense_id: int, field: str, value: Any) -> Optional[Dict[str, Any]]:
        for exp in self._expenses:
            if exp["id"] == expense_id:
                if field not in exp:
                    return None  # Invalid field
                if field == "currency" and value is None:
                    exp["currency"] = get_default_currency()
                else:
                    exp[field] = value
                self._save_json("expenses.json", self._expenses)
                return exp
        return None  # Not found

    def delete(self, expense_id: int) -> bool:
        for exp in self._expenses:
            if exp["id"] == expense_id:
                self._expenses[:] = [e for e in self._expenses if e["id"] != expense_id]
                self._save_json("expenses.json", self._expenses)
                return True
        return False

    def bulk_delete(self, ids: List[int]) -> int:
        before = len(self._expenses)
        self._expenses[:] = [e for e in self._expenses if e["id"] not in ids]
        deleted_count = before - len(self._expenses)
        self._save_json("expenses.json", self._expenses)
        return deleted_count


class PostgresExpenseRepository(ExpenseRepositoryInterface):
    """PostgreSQL-based expense repository."""

    def __init__(self):
        from app.core.db import get_db_session
        from app.core.models import Expense
        self._get_db_session = get_db_session
        self._model = Expense

    def list_all(self) -> List[Dict[str, Any]]:
        with self._get_db_session() as db:
            expenses = db.query(self._model).all()
            return [exp.to_dict() for exp in expenses]

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        
        with self._get_db_session() as db:
            expense = self._model(
                date=data.get("date"),
                business=data.get("business"),
                category=data.get("category"),
                amount=data.get("amount"),
                account=data.get("account"),
                currency=data.get("currency"),
                notes=data.get("notes"),
            )
            db.add(expense)
            db.flush()
            result = expense.to_dict()
            return result

    def update(self, expense_id: int, field: str, value: Any) -> Optional[Dict[str, Any]]:
        with self._get_db_session() as db:
            expense = db.query(self._model).filter(self._model.id == expense_id).first()
            if not expense:
                return None
            
            if not hasattr(expense, field):
                return None  # Invalid field
            
            if field == "currency" and value is None:
                value = get_default_currency()
            
            setattr(expense, field, value)
            db.flush()
            return expense.to_dict()

    def delete(self, expense_id: int) -> bool:
        with self._get_db_session() as db:
            expense = db.query(self._model).filter(self._model.id == expense_id).first()
            if not expense:
                return False
            db.delete(expense)
            return True

    def bulk_delete(self, ids: List[int]) -> int:
        with self._get_db_session() as db:
            deleted = db.query(self._model).filter(self._model.id.in_(ids)).delete(synchronize_session=False)
            return deleted
