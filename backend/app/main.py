from contextlib import asynccontextmanager
from fastapi import FastAPI
from .routers import expense_router, income_router, health_router
# from .core.db import init_db

# Use FastAPI lifespan instead of on_event hooks
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    # init_db()
    yield
    # Shutdown actions (if needed later)

app = FastAPI(title="Home Budget Web API", lifespan=lifespan)

# Register routers
# app.include_router(expense_router.router, prefix="/api/expenses", tags=["Expenses"])
# app.include_router(income_router.router, prefix="/api/incomes", tags=["Incomes"])
app.include_router(health_router.router, prefix="/api", tags=["Health"])
