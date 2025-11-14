from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import expense_router, income_router, health_router

app = FastAPI(title="Home Budget Web Backend")

# --- CORS: allow frontend (React on port 5080) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; restrict later in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health_router.router, prefix="/api")
app.include_router(expense_router.router, prefix="/api")
app.include_router(income_router.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Home Budget Web Backend running"}
