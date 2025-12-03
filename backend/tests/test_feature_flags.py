"""Tests for the feature flags module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.core.feature_flags import (get_flag_from_db, get_flag_from_env,
                                    is_feature_enabled)
from app.models.feature_flag import FeatureFlag


class TestGetFlagFromEnv:
    """Tests for environment variable-based flag evaluation."""

    def test_flag_enabled_true(self):
        """Flag should be enabled when env var is 'true'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "true"}):
            assert get_flag_from_env("TEST_FLAG") is True

    def test_flag_enabled_1(self):
        """Flag should be enabled when env var is '1'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "1"}):
            assert get_flag_from_env("TEST_FLAG") is True

    def test_flag_enabled_yes(self):
        """Flag should be enabled when env var is 'yes'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "yes"}):
            assert get_flag_from_env("TEST_FLAG") is True

    def test_flag_enabled_on(self):
        """Flag should be enabled when env var is 'on'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "on"}):
            assert get_flag_from_env("TEST_FLAG") is True

    def test_flag_disabled_false(self):
        """Flag should be disabled when env var is 'false'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "false"}):
            assert get_flag_from_env("TEST_FLAG") is False

    def test_flag_disabled_0(self):
        """Flag should be disabled when env var is '0'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "0"}):
            assert get_flag_from_env("TEST_FLAG") is False

    def test_flag_disabled_no(self):
        """Flag should be disabled when env var is 'no'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "no"}):
            assert get_flag_from_env("TEST_FLAG") is False

    def test_flag_disabled_off(self):
        """Flag should be disabled when env var is 'off'."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "off"}):
            assert get_flag_from_env("TEST_FLAG") is False

    def test_flag_not_set(self):
        """Flag should return None when env var is not set."""
        with patch.dict(os.environ, {}, clear=False):
            # Make sure the key doesn't exist
            os.environ.pop("FF_NONEXISTENT_FLAG", None)
            assert get_flag_from_env("NONEXISTENT_FLAG") is None

    def test_flag_case_insensitive(self):
        """Flag name should be case-insensitive."""
        with patch.dict(os.environ, {"FF_MY_FLAG": "true"}):
            assert get_flag_from_env("my_flag") is True
            assert get_flag_from_env("MY_FLAG") is True
            assert get_flag_from_env("My_Flag") is True

    def test_flag_value_case_insensitive(self):
        """Flag value should be case-insensitive."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "TRUE"}):
            assert get_flag_from_env("TEST_FLAG") is True
        with patch.dict(os.environ, {"FF_TEST_FLAG": "False"}):
            assert get_flag_from_env("TEST_FLAG") is False


class TestGetFlagFromDb:
    """Tests for database-based flag evaluation."""

    def test_global_flag_enabled(self):
        """Should return True for enabled global flag."""
        mock_db = MagicMock()
        mock_flag = FeatureFlag(name="TEST_FLAG", enabled=True, user_id=None)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_flag

        result = get_flag_from_db("TEST_FLAG", mock_db)
        assert result is True

    def test_global_flag_disabled(self):
        """Should return False for disabled global flag."""
        mock_db = MagicMock()
        mock_flag = FeatureFlag(name="TEST_FLAG", enabled=False, user_id=None)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_flag

        result = get_flag_from_db("TEST_FLAG", mock_db)
        assert result is False

    def test_flag_not_found(self):
        """Should return None when flag is not in database."""
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = get_flag_from_db("NONEXISTENT_FLAG", mock_db)
        assert result is None

    def test_db_error_returns_none(self):
        """Should return None when database query fails."""
        mock_db = MagicMock()
        mock_db.query.side_effect = Exception("DB connection error")

        result = get_flag_from_db("TEST_FLAG", mock_db)
        assert result is None


class TestIsFeatureEnabled:
    """Tests for the main is_feature_enabled function."""

    def test_env_takes_priority_over_default(self):
        """Environment variable should override default value."""
        with patch.dict(os.environ, {"FF_TEST_FLAG": "true"}):
            assert is_feature_enabled("TEST_FLAG", default=False) is True
        with patch.dict(os.environ, {"FF_TEST_FLAG": "false"}):
            assert is_feature_enabled("TEST_FLAG", default=True) is False

    def test_default_when_flag_not_set(self):
        """Should return default when flag is not set anywhere."""
        os.environ.pop("FF_MISSING_FLAG", None)
        assert is_feature_enabled("MISSING_FLAG", default=True) is True
        assert is_feature_enabled("MISSING_FLAG", default=False) is False

    def test_default_is_false(self):
        """Default should be False when not specified."""
        os.environ.pop("FF_MISSING_FLAG", None)
        assert is_feature_enabled("MISSING_FLAG") is False

    def test_env_takes_priority_over_db(self):
        """Environment variable should override database value."""
        mock_db = MagicMock()
        mock_flag = FeatureFlag(name="TEST_FLAG", enabled=True, user_id=None)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_flag

        with patch.dict(os.environ, {"FF_TEST_FLAG": "false"}):
            result = is_feature_enabled("TEST_FLAG", db=mock_db)
            assert result is False

    def test_db_used_when_env_not_set(self):
        """Database value should be used when env var is not set."""
        os.environ.pop("FF_DB_FLAG", None)

        mock_db = MagicMock()
        mock_flag = FeatureFlag(name="DB_FLAG", enabled=True, user_id=None)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_flag

        result = is_feature_enabled("DB_FLAG", db=mock_db)
        assert result is True


class TestFeatureFlagModel:
    """Tests for the FeatureFlag model."""

    def test_repr_global_flag(self):
        """Should have correct repr for global flag."""
        flag = FeatureFlag(name="TEST", enabled=True, user_id=None)
        assert "TEST" in repr(flag)
        assert "enabled=True" in repr(flag)
        assert "global" in repr(flag)

    def test_repr_user_flag(self):
        """Should have correct repr for user-specific flag."""
        flag = FeatureFlag(name="TEST", enabled=False, user_id=42)
        assert "TEST" in repr(flag)
        assert "enabled=False" in repr(flag)
        assert "user_id=42" in repr(flag)
