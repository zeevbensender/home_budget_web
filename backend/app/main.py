from fastapi import FastAPI
from .routers import expense_router, income_router
from .core.db import init_db

app = FastAPI(title="Home Budget Web API")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(expense_router.router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(income_router.router, prefix="/api/incomes", tags=["Incomes"])

