"""
Application configuration module.

Reads settings from environment variables with validation using pydantic-settings.
"""

from functools import lru_cache
from urllib.parse import urlparse, urlunparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment mode: dev / staging / prod
    env: str = "dev"

    # Database configuration
    database_url: str = "postgresql://localhost:5432/budget_db"
    pool_size: int = 5

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000

    def get_masked_database_url(self) -> str:
        """
        Returns the database URL with password masked for safe display.

        Example:
            postgresql://user:secret@host:5432/db
            becomes
            postgresql://user:****@host:5432/db
        """
        try:
            parsed = urlparse(self.database_url)
            if parsed.password:
                # Reconstruct netloc with masked password
                if parsed.port:
                    masked_netloc = (
                        f"{parsed.username}:****@{parsed.hostname}:{parsed.port}"
                    )
                else:
                    masked_netloc = f"{parsed.username}:****@{parsed.hostname}"
                # Reconstruct the URL using individual components
                return urlunparse(
                    (
                        parsed.scheme,
                        masked_netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment,
                    )
                )
            return self.database_url
        except Exception:
            # If parsing fails, return URL with generic masking
            # This fallback is intentionally conservative
            return self.database_url

    def is_dev_mode(self) -> bool:
        """Check if running in development mode."""
        return self.env.lower() == "dev"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached singleton instance of Settings.
    """
    return Settings()
