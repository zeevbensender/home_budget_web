import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import expense_router, income_router, health_router, config_router

app = FastAPI(title="Home Budget Web Backend")

# CORS for frontend (React from any host during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # restrict later for Prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router.router, prefix="/api/v1")
app.include_router(expense_router.router, prefix="/api/v1")
app.include_router(income_router.router, prefix="/api/v1")
app.include_router(config_router.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Home Budget Web Backend running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)