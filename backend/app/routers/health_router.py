from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check():
    """
    Basic health check endpoint.
    Returns 200 OK if the application is running.
    """
    return {"status": "ok"}
