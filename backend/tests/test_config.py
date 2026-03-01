"""
Test Suite for Configuration Management
========================================
Tests the centralized Config class to ensure configuration is valid
and demonstrates OOP testing patterns.
"""

import pytest
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config


class TestConfigDefaults:
    """Test default configuration values"""

    def test_database_url_default(self):
        """Test default database URL"""
        assert Config.DATABASE_URL == "sqlite:///./fraud_detection.db"

    def test_model_dir_default(self):
        """Test default model directory"""
        assert Config.MODEL_DIR == "model_artifacts"

    def test_api_defaults(self):
        """Test API configuration defaults"""
        assert Config.API_HOST == "0.0.0.0"
        assert Config.API_PORT == 8000
        assert Config.API_RELOAD == True


class TestFraudThresholds:
    """Test fraud detection threshold configuration"""

    def test_fraud_thresholds_exist(self):
        """Test that all expected fraud thresholds are defined"""
        required_thresholds = [
            "amount_critical",
            "amount_high",
            "amount_medium",
            "distance_suspicious"
        ]
        for threshold in required_thresholds:
            assert threshold in Config.FRAUD_THRESHOLDS

    def test_fraud_thresholds_are_numbers(self):
        """Test that fraud thresholds are numeric"""
        for key, value in Config.FRAUD_THRESHOLDS.items():
            assert isinstance(value, (int, float)), f"{key} should be numeric"
            assert value > 0, f"{key} should be positive"

    def test_amount_thresholds_ordered(self):
        """Test that amount thresholds are in descending order"""
        assert (Config.FRAUD_THRESHOLDS["amount_critical"] >
                Config.FRAUD_THRESHOLDS["amount_high"] >
                Config.FRAUD_THRESHOLDS["amount_medium"])

    def test_fraud_score_weights_exist(self):
        """Test that all fraud score weights are defined"""
        required_weights = [
            "amount_critical",
            "amount_high",
            "amount_medium",
            "international",
            "distance",
            "unusual_hour",
            "online_high_amount",
            "risk_factor_bonus"
        ]
        for weight in required_weights:
            assert weight in Config.FRAUD_SCORE_WEIGHTS

    def test_fraud_score_weights_valid_range(self):
        """Test that fraud score weights are in valid range [0, 1]"""
        for key, value in Config.FRAUD_SCORE_WEIGHTS.items():
            assert 0 <= value <= 1, f"{key} weight should be between 0 and 1"


class TestRiskThresholds:
    """Test risk level classification thresholds"""

    def test_risk_thresholds_exist(self):
        """Test that all risk level thresholds are defined"""
        required_thresholds = ["critical", "high", "medium", "low"]
        for threshold in required_thresholds:
            assert threshold in Config.RISK_THRESHOLDS

    def test_risk_thresholds_in_valid_range(self):
        """Test that risk thresholds are between 0 and 1"""
        for key, value in Config.RISK_THRESHOLDS.items():
            assert 0 <= value <= 1, f"Risk threshold {key} should be between 0 and 1"

    def test_risk_thresholds_ordered(self):
        """Test that risk thresholds are in descending order"""
        assert (Config.RISK_THRESHOLDS["critical"] >
                Config.RISK_THRESHOLDS["high"] >
                Config.RISK_THRESHOLDS["medium"] >
                Config.RISK_THRESHOLDS["low"])


class TestModelConfiguration:
    """Test ML model configuration"""

    def test_model_paths_constructed(self):
        """Test that model paths are properly constructed"""
        assert Config.MODEL_PATH == os.path.join(Config.MODEL_DIR, "model.pkl")
        assert Config.SCALER_PATH == os.path.join(Config.MODEL_DIR, "scaler.pkl")
        assert Config.FEATURES_PATH == os.path.join(Config.MODEL_DIR, "features.pkl")

    def test_expected_feature_counts(self):
        """Test expected feature counts are defined"""
        assert Config.EXPECTED_V_FEATURE_COUNT == 28
        assert Config.EXPECTED_FINAL_FEATURE_COUNT == 57

    def test_prediction_threshold_multiplier(self):
        """Test prediction threshold multiplier is in valid range"""
        assert 0 < Config.PREDICTION_THRESHOLD_MULTIPLIER <= 1.5

    def test_risk_score_multiplier(self):
        """Test risk score multiplier is positive"""
        assert Config.RISK_SCORE_MULTIPLIER > 0
        assert isinstance(Config.RISK_SCORE_MULTIPLIER, int)


class TestCORSConfiguration:
    """Test CORS configuration"""

    def test_cors_origins_is_list(self):
        """Test that CORS origins is a list"""
        assert isinstance(Config.CORS_ORIGINS, list)

    def test_cors_methods_defined(self):
        """Test that CORS methods are defined"""
        assert isinstance(Config.CORS_ALLOW_METHODS, list)

    def test_cors_headers_defined(self):
        """Test that CORS headers are defined"""
        assert isinstance(Config.CORS_ALLOW_HEADERS, list)


class TestAuthConfiguration:
    """Test authentication configuration (for Phase 3)"""

    def test_secret_key_exists(self):
        """Test that secret key is defined"""
        assert Config.SECRET_KEY is not None
        assert len(Config.SECRET_KEY) > 0

    def test_algorithm_defined(self):
        """Test that JWT algorithm is defined"""
        assert Config.ALGORITHM == "HS256"

    def test_token_expire_time(self):
        """Test that token expiration time is positive"""
        assert Config.ACCESS_TOKEN_EXPIRE_MINUTES > 0


class TestEnvironmentMethods:
    """Test environment detection methods"""

    def test_is_development(self):
        """Test is_development() method"""
        # Default environment is development
        assert Config.is_development() == True

    def test_is_production(self):
        """Test is_production() method"""
        # Default environment is not production
        assert Config.is_production() == False

    def test_environment_variable(self):
        """Test environment variable reading"""
        assert Config.ENVIRONMENT in ["development", "production", "testing"]


class TestConfigValidation:
    """Test configuration validation methods"""

    def test_validate_config_with_valid_model(self):
        """Test that validate_config works when model exists"""
        try:
            Config.validate_config()
            # If we get here, validation passed
            assert True
        except FileNotFoundError:
            # Model files might not exist in test environment - that's okay
            pytest.skip("Model files not found - expected in test environment")

    def test_get_summary(self):
        """Test that get_summary() returns a dictionary"""
        summary = Config.get_summary()
        assert isinstance(summary, dict)
        assert "environment" in summary
        assert "database_url" in summary
        assert "model_dir" in summary
        assert "api_host" in summary
        assert "api_port" in summary

    def test_summary_excludes_secrets(self):
        """Test that summary doesn't expose SECRET_KEY"""
        summary = Config.get_summary()
        assert "secret_key" not in summary


class TestConfigOverrideWithEnvVars:
    """Test configuration override using environment variables"""

    def test_can_override_database_url(self, monkeypatch):
        """Test that DATABASE_URL can be overridden via env var"""
        test_db_url = "sqlite:///./test_database.db"
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        # Reimport to pick up new env var
        import importlib
        import config as config_module
        importlib.reload(config_module)

        assert config_module.Config.DATABASE_URL == test_db_url

    def test_can_override_api_port(self, monkeypatch):
        """Test that API_PORT can be overridden via env var"""
        monkeypatch.setenv("API_PORT", "9000")

        import importlib
        import config as config_module
        importlib.reload(config_module)

        assert config_module.Config.API_PORT == 9000


class TestPaginationConfiguration:
    """Test pagination settings"""

    def test_default_page_size(self):
        """Test default page size is reasonable"""
        assert 10 <= Config.DEFAULT_PAGE_SIZE <= 1000

    def test_max_page_size(self):
        """Test max page size is larger than default"""
        assert Config.MAX_PAGE_SIZE >= Config.DEFAULT_PAGE_SIZE


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '--tb=short'])
