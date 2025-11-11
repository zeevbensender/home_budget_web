from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health_router, expense_router, income_router

# Create FastAPI instance
app = FastAPI(title="Home Budget Web API")

# --- CORS middleware ---
# Allows frontend (port 5080 or any domain) to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later restrict this list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(health_router.router, prefix="/api", tags=["health"])
app.include_router(expense_router.router, prefix="/api", tags=["expenses"])
app.include_router(income_router.router, prefix="/api", tags=["income"])

# --- Root route (optional, for sanity check) ---
@app.get("/")
def root():
    return {"message": "Home Budget Web backend running"}


# --- Entry point (for local dev only) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
