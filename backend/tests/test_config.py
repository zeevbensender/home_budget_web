"""Tests for the configuration module and config router."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

client = TestClient(app)


class TestMaskedDatabaseUrl:
    """Tests for the get_masked_database_url method."""

    def test_mask_password_in_url(self):
        """Ensure password is masked in database URL."""
        settings = Settings(
            database_url="postgresql://user:secret123@localhost:5432/mydb"
        )
        masked = settings.get_masked_database_url()
        assert "secret123" not in masked
        assert "****" in masked
        assert "user" in masked
        assert "localhost:5432/mydb" in masked

    def test_no_password_in_url(self):
        """URL without password should remain unchanged."""
        settings = Settings(database_url="postgresql://localhost:5432/mydb")
        masked = settings.get_masked_database_url()
        assert masked == "postgresql://localhost:5432/mydb"

    def test_complex_password_characters(self):
        """Password with special characters should be masked correctly."""
        settings = Settings(
            database_url="postgresql://user:p@ss!word#123@localhost:5432/mydb"
        )
        masked = settings.get_masked_database_url()
        assert "p@ss!word#123" not in masked
        assert "****" in masked


class TestIsDevMode:
    """Tests for the is_dev_mode method."""

    def test_dev_mode_lowercase(self):
        """Should return True for 'dev' environment."""
        settings = Settings(env="dev")
        assert settings.is_dev_mode() is True

    def test_dev_mode_uppercase(self):
        """Should return True for 'DEV' environment (case insensitive)."""
        settings = Settings(env="DEV")
        assert settings.is_dev_mode() is True

    def test_prod_mode(self):
        """Should return False for 'prod' environment."""
        settings = Settings(env="prod")
        assert settings.is_dev_mode() is False

    def test_staging_mode(self):
        """Should return False for 'staging' environment."""
        settings = Settings(env="staging")
        assert settings.is_dev_mode() is False


class TestConfigShowEndpoint:
    """Tests for the /api/v1/config/show endpoint."""

    def test_config_show_in_dev_mode(self):
        """Config show endpoint should work in dev mode."""
        # Clear the cached settings
        get_settings.cache_clear()

        with patch.dict(
            os.environ,
            {
                "ENV": "dev",
                "DATABASE_URL": "postgresql://user:secret@localhost:5432/testdb",
                "POOL_SIZE": "10",
            },
        ):
            get_settings.cache_clear()
            response = client.get("/api/v1/config/show")
            assert response.status_code == 200
            data = response.json()
            assert data["env"] == "dev"
            assert "****" in data["database_url"]
            assert "secret" not in data["database_url"]
            assert data["pool_size"] == 10

        # Reset cache after test
        get_settings.cache_clear()

    def test_config_show_blocked_in_prod_mode(self):
        """Config show endpoint should be blocked in prod mode."""
        get_settings.cache_clear()

        with patch.dict(os.environ, {"ENV": "prod"}):
            get_settings.cache_clear()
            response = client.get("/api/v1/config/show")
            assert response.status_code == 403
            assert "dev mode" in response.json()["detail"].lower()

        # Reset cache after test
        get_settings.cache_clear()


class TestSettingsDefaults:
    """Tests for default settings values."""

    def test_default_pool_size(self):
        """Default pool size should be 5."""
        settings = Settings()
        assert settings.pool_size == 5

    def test_default_env(self):
        """Default environment should be 'dev'."""
        settings = Settings()
        assert settings.env == "dev"
