"""
Configuration router for displaying application settings.
"""

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings

router = APIRouter()


@router.get("/config/show", tags=["Config"])
def config_show():
    """
    Display application configuration with masked sensitive values.

    Only available in dev mode. Returns masked DATABASE_URL and other settings.
    """
    settings = get_settings()

    if not settings.is_dev_mode():
        raise HTTPException(
            status_code=403,
            detail="Configuration display is only available in dev mode",
        )

    return {
        "env": settings.env,
        "database_url": settings.get_masked_database_url(),
        "pool_size": settings.pool_size,
        "host": settings.host,
        "port": settings.port,
    }
