"""Repository layer for income operations."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.core.settings import get_default_currency
from app.core.storage import load_json, save_json


class IncomeRepositoryInterface(ABC):
    """Abstract interface for income repository."""

    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all incomes."""
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new income."""
        pass

    @abstractmethod
    def update(self, income_id: int, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Update an income field."""
        pass

    @abstractmethod
    def delete(self, income_id: int) -> bool:
        """Delete an income."""
        pass

    @abstractmethod
    def bulk_delete(self, ids: List[int]) -> int:
        """Bulk delete incomes. Returns the count of deleted items."""
        pass


class JsonIncomeRepository(IncomeRepositoryInterface):
    """JSON-based income repository."""

    def __init__(self, storage_module):
        self._load_json = load_json
        self._save_json = save_json
        self._incomes = load_json("incomes.json", [
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

    def list_all(self) -> List[Dict[str, Any]]:
        return self._incomes

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = max([i["id"] for i in self._incomes], default=0) + 1
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        data["id"] = new_id
        self._incomes.append(data)
        self._save_json("incomes.json", self._incomes)
        return data

    def update(self, income_id: int, field: str, value: Any) -> Optional[Dict[str, Any]]:
        for inc in self._incomes:
            if inc["id"] == income_id:
                if field not in inc:
                    return None  # Invalid field
                if field == "currency" and value is None:
                    inc["currency"] = get_default_currency()
                else:
                    inc[field] = value
                self._save_json("incomes.json", self._incomes)
                return inc
        return None  # Not found

    def delete(self, income_id: int) -> bool:
        for inc in self._incomes:
            if inc["id"] == income_id:
                self._incomes[:] = [i for i in self._incomes if i["id"] != income_id]
                self._save_json("incomes.json", self._incomes)
                return True
        return False

    def bulk_delete(self, ids: List[int]) -> int:
        before = len(self._incomes)
        self._incomes[:] = [i for i in self._incomes if i["id"] not in ids]
        deleted_count = before - len(self._incomes)
        self._save_json("incomes.json", self._incomes)
        return deleted_count


class PostgresIncomeRepository(IncomeRepositoryInterface):
    """PostgreSQL-based income repository."""

    def __init__(self):
        from app.core.db import get_db_session
        from app.core.models import Income
        self._get_db_session = get_db_session
        self._model = Income

    def list_all(self) -> List[Dict[str, Any]]:
        with self._get_db_session() as db:
            incomes = db.query(self._model).all()
            return [inc.to_dict() for inc in incomes]

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("currency"):
            data["currency"] = get_default_currency()
        
        with self._get_db_session() as db:
            income = self._model(
                date=data.get("date"),
                category=data.get("category"),
                amount=data.get("amount"),
                account=data.get("account"),
                currency=data.get("currency"),
                notes=data.get("notes"),
            )
            db.add(income)
            db.flush()
            result = income.to_dict()
            return result

    def update(self, income_id: int, field: str, value: Any) -> Optional[Dict[str, Any]]:
        with self._get_db_session() as db:
            income = db.query(self._model).filter(self._model.id == income_id).first()
            if not income:
                return None
            
            if not hasattr(income, field):
                return None  # Invalid field
            
            if field == "currency" and value is None:
                value = get_default_currency()
            
            setattr(income, field, value)
            db.flush()
            return income.to_dict()

    def delete(self, income_id: int) -> bool:
        with self._get_db_session() as db:
            income = db.query(self._model).filter(self._model.id == income_id).first()
            if not income:
                return False
            db.delete(income)
            return True

    def bulk_delete(self, ids: List[int]) -> int:
        with self._get_db_session() as db:
            deleted = db.query(self._model).filter(self._model.id.in_(ids)).delete(synchronize_session=False)
            return deleted
