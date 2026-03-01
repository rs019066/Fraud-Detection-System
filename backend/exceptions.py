"""
Custom Exception Hierarchy for Fraud Detection System
======================================================
Demonstrates proper OOP exception design with inheritance hierarchy.

Benefits of custom exceptions:
1. More specific error handling (catch ModelLoadException vs generic Exception)
2. Better error messages with domain-specific context
3. Easier debugging (exception type tells you what went wrong)
4. Demonstrates inheritance and polymorphism

Exception Hierarchy:
--------------------
FraudDetectionException (base)
├── ModelException
│   ├── ModelLoadException
│   └── PredictionException
├── DataException
│   ├── InvalidTransactionException
│   ├── FeatureEngineeringException
│   └── MissingFeatureException
├── DatabaseException
│   ├── TransactionNotFoundException
│   └── DatabaseConnectionException
└── AuthenticationException (for Phase 3)
    ├── InvalidCredentialsException
    └── TokenExpiredException
"""

from typing import Optional, Dict, Any


class FraudDetectionException(Exception):
    """
    Base exception for all fraud detection system errors.

    All custom exceptions inherit from this, allowing catch-all error handling
    while still enabling specific exception catching when needed.

    Example:
        try:
            model.predict(transaction)
        except ModelLoadException:
            # Handle model loading specifically
            pass
        except FraudDetectionException:
            # Catch any other fraud detection error
            pass
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error description
            details: Additional context (e.g., {'transaction_id': 123, 'error_code': 'E001'})
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        """String representation of exception"""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON API responses.

        Useful for FastAPI exception handlers that return JSON error responses.
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


# ============================================================================
# Model-Related Exceptions
# ============================================================================

class ModelException(FraudDetectionException):
    """Base exception for ML model-related errors"""
    pass


class ModelLoadException(ModelException):
    """
    Raised when model artifacts cannot be loaded from disk.

    Common causes:
    - Model files missing (model.pkl, scaler.pkl, features.pkl)
    - Corrupted pickle files
    - Version mismatch (model trained with different sklearn version)
    """

    def __init__(self, model_path: str, original_error: Optional[Exception] = None):
        message = f"Failed to load model from {model_path}"
        details = {
            "model_path": model_path,
            "original_error": str(original_error) if original_error else None
        }
        super().__init__(message, details)


class PredictionException(ModelException):
    """
    Raised when model prediction fails.

    Common causes:
    - Feature shape mismatch (wrong number of features)
    - NaN or infinite values in features
    - Model not fitted yet
    """

    def __init__(self, reason: str, transaction_data: Optional[Dict] = None):
        message = f"Prediction failed: {reason}"
        details = {"transaction_data": transaction_data} if transaction_data else {}
        super().__init__(message, details)


# ============================================================================
# Data-Related Exceptions
# ============================================================================

class DataException(FraudDetectionException):
    """Base exception for data validation and processing errors"""
    pass


class InvalidTransactionException(DataException):
    """
    Raised when transaction data is invalid.

    Common causes:
    - Missing required fields
    - Invalid field types (string where number expected)
    - Out-of-range values (negative amount, hour > 23)
    """

    def __init__(self, field_name: str, field_value: Any, reason: str):
        message = f"Invalid transaction field '{field_name}': {reason}"
        details = {
            "field_name": field_name,
            "field_value": field_value,
            "reason": reason
        }
        super().__init__(message, details)


class FeatureEngineeringException(DataException):
    """
    Raised when feature engineering fails.

    Common causes:
    - Unable to map transaction to V-features
    - NaN values after feature engineering
    - Feature count mismatch (expected 57, got different number)
    """

    def __init__(self, stage: str, reason: str):
        message = f"Feature engineering failed at stage '{stage}': {reason}"
        details = {"stage": stage, "reason": reason}
        super().__init__(message, details)


class MissingFeatureException(DataException):
    """
    Raised when expected features are missing.

    Common causes:
    - Feature engineering pipeline didn't generate all expected features
    - Model expects different feature set than provided
    """

    def __init__(self, expected_features: list, actual_features: list):
        missing = set(expected_features) - set(actual_features)
        message = f"Missing {len(missing)} features: {list(missing)[:5]}..."
        details = {
            "expected_count": len(expected_features),
            "actual_count": len(actual_features),
            "missing_features": list(missing)
        }
        super().__init__(message, details)


# ============================================================================
# Database-Related Exceptions
# ============================================================================

class DatabaseException(FraudDetectionException):
    """Base exception for database operations"""
    pass


class TransactionNotFoundException(DatabaseException):
    """
    Raised when a requested transaction doesn't exist in database.
    """

    def __init__(self, transaction_id: int):
        message = f"Transaction with ID {transaction_id} not found"
        details = {"transaction_id": transaction_id}
        super().__init__(message, details)


class DatabaseConnectionException(DatabaseException):
    """
    Raised when database connection fails.

    Common causes:
    - Database file not accessible
    - Connection pool exhausted
    - Database locked by another process
    """

    def __init__(self, reason: str):
        message = f"Database connection failed: {reason}"
        super().__init__(message)


# ============================================================================
# Authentication Exceptions (for Phase 3)
# ============================================================================

class AuthenticationException(FraudDetectionException):
    """Base exception for authentication and authorization errors"""
    pass


class InvalidCredentialsException(AuthenticationException):
    """
    Raised when login credentials are incorrect.
    """

    def __init__(self, username: str):
        message = "Invalid username or password"
        details = {"username": username}
        super().__init__(message, details)


class TokenExpiredException(AuthenticationException):
    """
    Raised when JWT token has expired.
    """

    def __init__(self):
        message = "Authentication token has expired. Please login again."
        super().__init__(message)


class InsufficientPermissionsException(AuthenticationException):
    """
    Raised when user doesn't have permission for requested action.

    Example: Regular user trying to access admin-only endpoint
    """

    def __init__(self, required_role: str, user_role: str):
        message = f"Insufficient permissions. Required: {required_role}, User has: {user_role}"
        details = {"required_role": required_role, "user_role": user_role}
        super().__init__(message, details)


# ============================================================================
# Configuration Exception
# ============================================================================

class ConfigurationException(FraudDetectionException):
    """
    Raised when system configuration is invalid.

    Common causes:
    - Missing environment variables
    - Invalid configuration values
    - Model artifacts not found
    """

    def __init__(self, config_key: str, reason: str):
        message = f"Invalid configuration for '{config_key}': {reason}"
        details = {"config_key": config_key, "reason": reason}
        super().__init__(message, details)


# ============================================================================
# Utility Functions
# ============================================================================

def handle_exception(exc: Exception) -> Dict[str, Any]:
    """
    Convert any exception to a dictionary for API responses.

    For custom exceptions, uses to_dict(). For built-in exceptions,
    creates a basic error dict.

    Args:
        exc: Exception to handle

    Returns:
        Dictionary with error information
    """
    if isinstance(exc, FraudDetectionException):
        return exc.to_dict()
    else:
        # Handle built-in Python exceptions
        return {
            "error_type": exc.__class__.__name__,
            "message": str(exc),
            "details": {}
        }


if __name__ == "__main__":
    # Demonstrate exception hierarchy
    print("Exception Hierarchy Demonstration:\n")

    # Example 1: Model loading failure
    try:
        raise ModelLoadException("/path/to/model.pkl", ValueError("Corrupted file"))
    except ModelLoadException as e:
        print(f"❌ {e}")
        print(f"   Dict: {e.to_dict()}\n")

    # Example 2: Invalid transaction
    try:
        raise InvalidTransactionException("transaction_amount", -100, "Amount cannot be negative")
    except InvalidTransactionException as e:
        print(f"❌ {e}")
        print(f"   Dict: {e.to_dict()}\n")

    # Example 3: Transaction not found
    try:
        raise TransactionNotFoundException(12345)
    except TransactionNotFoundException as e:
        print(f"❌ {e}")
        print(f"   Dict: {e.to_dict()}\n")

    # Example 4: Catching base exception
    try:
        raise PredictionException("Feature shape mismatch", {"expected": 57, "got": 50})
    except FraudDetectionException as e:
        print(f"❌ Caught via base class: {e}")
        print(f"   Type: {type(e).__name__}")
