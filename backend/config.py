"""
Configuration Management for Fraud Detection System
===================================================
Centralized configuration using environment variables with sensible defaults.

This demonstrates the Single Responsibility Principle (SRP) - configuration
is separated from business logic and kept in one place.

Benefits:
- Easy to change settings without modifying code
- Environment-specific configurations (dev, test, prod)
- No magic numbers scattered throughout codebase
- Type-safe access to configuration values
"""

import os
from typing import Dict
from pathlib import Path


class Config:
    """
    Centralized configuration class for the fraud detection system.

    Uses environment variables when available, falls back to sensible defaults.
    All configuration values are accessed as class attributes for easy mocking in tests.
    """

    # ============================================================================
    # Database Configuration
    # ============================================================================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./fraud_detection.db"
    )

    # ============================================================================
    # Model Configuration
    # ============================================================================
    MODEL_DIR: str = os.getenv(
        "MODEL_DIR",
        "model_artifacts"
    )

    MODEL_PATH: str = os.path.join(MODEL_DIR, "model.pkl")
    SCALER_PATH: str = os.path.join(MODEL_DIR, "scaler.pkl")
    FEATURES_PATH: str = os.path.join(MODEL_DIR, "features.pkl")
    MODEL_CONFIG_PATH: str = os.path.join(MODEL_DIR, "model_config.json")

    # ============================================================================
    # Fraud Scoring Thresholds
    # ============================================================================
    # These thresholds define what makes a transaction suspicious.
    # In production, these would be tuned based on historical fraud data
    # and business requirements (false positive tolerance vs fraud catch rate).

    FRAUD_THRESHOLDS: Dict[str, float] = {
        "amount_critical": float(os.getenv("FRAUD_AMOUNT_CRITICAL", "5000.0")),  # > $5000
        "amount_high": float(os.getenv("FRAUD_AMOUNT_HIGH", "2000.0")),          # > $2000
        "amount_medium": float(os.getenv("FRAUD_AMOUNT_MEDIUM", "1000.0")),      # > $1000
        "distance_suspicious": float(os.getenv("FRAUD_DISTANCE_SUSPICIOUS", "1000.0")),  # > 1000km
    }

    FRAUD_SCORE_WEIGHTS: Dict[str, float] = {
        "amount_critical": 0.3,      # Weight for transactions > $5000
        "amount_high": 0.2,          # Weight for transactions > $2000
        "amount_medium": 0.1,        # Weight for transactions > $1000
        "international": 0.25,       # Weight for international transactions
        "distance": 0.2,             # Weight for far-from-home transactions
        "unusual_hour": 0.15,        # Weight for 12am-4am transactions
        "online_high_amount": 0.15,  # Weight for online + high amount combo
        "risk_factor_bonus": 0.1,    # Bonus when 3+ risk factors present
    }

    # ============================================================================
    # Risk Level Classification Thresholds
    # ============================================================================
    # Maps fraud probability to human-readable risk levels.
    # These thresholds affect what alerts are shown to users/admins.

    RISK_THRESHOLDS: Dict[str, float] = {
        "critical": float(os.getenv("RISK_CRITICAL", "0.8")),    # >= 80% probability
        "high": float(os.getenv("RISK_HIGH", "0.6")),            # >= 60% probability
        "medium": float(os.getenv("RISK_MEDIUM", "0.4")),        # >= 40% probability
        "low": float(os.getenv("RISK_LOW", "0.2")),              # >= 20% probability
        # < 20% is "minimal"
    }

    # ============================================================================
    # API Configuration
    # ============================================================================
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "True").lower() == "true"

    # CORS Configuration
    # WARNING: allow_origins=["*"] is insecure for production!
    # In production, specify exact frontend domains: ["https://fraud-detection.example.com"]
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # ============================================================================
    # ML Model Prediction Configuration
    # ============================================================================
    # Threshold adjustment factor for production (tune based on ROC curve analysis)
    # The model's default threshold is 0.5, but we multiply by 0.8 to get 0.4
    # to catch more frauds at the cost of slightly more false alarms.
    PREDICTION_THRESHOLD_MULTIPLIER: float = float(
        os.getenv("PREDICTION_THRESHOLD_MULTIPLIER", "0.8")
    )

    # Risk score calculation: probability * 120 capped at 100
    # Why 120? Allows probabilities around 0.83+ to hit max score of 100
    RISK_SCORE_MULTIPLIER: int = int(os.getenv("RISK_SCORE_MULTIPLIER", "120"))

    # ============================================================================
    # Authentication Configuration (for Phase 3)
    # ============================================================================
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # ============================================================================
    # Pagination Defaults
    # ============================================================================
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "1000"))

    # ============================================================================
    # Feature Engineering Configuration
    # ============================================================================
    EXPECTED_V_FEATURE_COUNT: int = 28  # V1-V28
    EXPECTED_FINAL_FEATURE_COUNT: int = 57  # After engineering

    # ============================================================================
    # Development/Testing Configuration
    # ============================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT.lower() == "development"

    @classmethod
    def validate_config(cls) -> None:
        """
        Validate configuration values.
        Raises ValueError if configuration is invalid.

        Useful for catching misconfiguration at startup rather than at runtime.
        """
        # Check that model files exist
        model_path = Path(cls.MODEL_PATH)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {cls.MODEL_PATH}. "
                "Run train_model.py to generate model artifacts."
            )

        # Validate thresholds are in valid ranges
        for key, value in cls.RISK_THRESHOLDS.items():
            if not 0 <= value <= 1:
                raise ValueError(
                    f"Risk threshold '{key}' must be between 0 and 1, got {value}"
                )

        # Validate threshold ordering (critical > high > medium > low)
        if not (cls.RISK_THRESHOLDS["critical"] > cls.RISK_THRESHOLDS["high"] >
                cls.RISK_THRESHOLDS["medium"] > cls.RISK_THRESHOLDS["low"]):
            raise ValueError("Risk thresholds must be in descending order")

        # Security check for production
        if cls.is_production():
            if cls.SECRET_KEY == "your-secret-key-change-this-in-production-use-openssl-rand-hex-32":
                raise ValueError(
                    "SECRET_KEY must be changed in production! "
                    "Generate a secure key with: openssl rand -hex 32"
                )
            if "*" in cls.CORS_ORIGINS:
                raise ValueError(
                    "CORS_ORIGINS cannot be '*' in production! "
                    "Specify exact frontend domains."
                )

    @classmethod
    def get_summary(cls) -> Dict[str, any]:
        """
        Get a summary of current configuration (for debugging/logging).
        Excludes sensitive values like SECRET_KEY.
        """
        return {
            "environment": cls.ENVIRONMENT,
            "database_url": cls.DATABASE_URL.split("://")[0] + "://...",  # Hide path
            "model_dir": cls.MODEL_DIR,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
            "cors_origins": cls.CORS_ORIGINS,
            "debug": cls.DEBUG,
            "risk_thresholds": cls.RISK_THRESHOLDS,
        }


# Singleton instance for easy import
config = Config()


if __name__ == "__main__":
    # Print configuration summary when run directly
    import json
    print("Current Configuration:")
    print(json.dumps(Config.get_summary(), indent=2))

    try:
        Config.validate_config()
        print("\n✅ Configuration is valid")
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}")
