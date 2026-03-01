"""
User Database Model
===================
SQLAlchemy model for user authentication and authorization.

Demonstrates:
- Database modeling with SQLAlchemy ORM
- User authentication schema
- Role-based access control (RBAC) foundation
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from typing import Optional

# Base will be imported from main.py to avoid circular imports
# This is defined when the model is registered with the database


class UserDB:
    """
    User model for authentication and authorization.

    Fields:
    - id: Primary key
    - username: Unique username for login
    - email: User email (unique)
    - hashed_password: Bcrypt-hashed password (never store plain text!)
    - role: User role ('admin' or 'analyst')
    - is_active: Whether user account is enabled
    - created_at: Account creation timestamp
    - last_login: Last successful login timestamp

    Roles:
    - 'admin': Full access - can view all transactions, delete, manage users, view statistics
    - 'analyst': Limited access - can submit transactions, view own history, search own transactions
    """

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Credentials
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Role-based access control
    role = Column(String, nullable=False, default="analyst")  # 'admin' or 'analyst'

    # Account status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        """String representation of user"""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"

    def is_analyst(self) -> bool:
        """Check if user has analyst role"""
        return self.role == "analyst"

    def update_last_login(self):
        """Update last login timestamp to current time"""
        self.last_login = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        Convert user to dictionary (for API responses).

        IMPORTANT: Never include hashed_password in API responses!
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


class UserCreate:
    """
    Model for user creation validation.

    In a real app, this would be a Pydantic BaseModel.
    Used for validating user registration data.
    """

    def __init__(self, username: str, email: str, password: str, role: str = "analyst"):
        self.username = username
        self.email = email
        self.password = password  # Plain text password (will be hashed)
        self.role = role

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate user creation data.

        Returns:
            (is_valid, error_message)
        """
        # Username validation
        if not self.username or len(self.username) < 3:
            return False, "Username must be at least 3 characters"
        if len(self.username) > 50:
            return False, "Username must be less than 50 characters"

        # Email validation (basic)
        if not self.email or "@" not in self.email:
            return False, "Invalid email address"

        # Password validation
        if not self.password or len(self.password) < 6:
            return False, "Password must be at least 6 characters"

        # Role validation
        if self.role not in ["admin", "analyst"]:
            return False, "Role must be 'admin' or 'analyst'"

        return True, None


class UserLogin:
    """
    Model for user login credentials.

    Simple class to hold login data.
    """
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


# Example usage and documentation
if __name__ == "__main__":
    print("User Model Documentation")
    print("=" * 50)
    print()
    print("UserDB Fields:")
    print("  - id: Primary key (auto-increment)")
    print("  - username: Unique username for login")
    print("  - email: User email (unique)")
    print("  - hashed_password: Bcrypt-hashed password")
    print("  - role: 'admin' or 'analyst'")
    print("  - is_active: Account enabled/disabled")
    print("  - created_at: Account creation timestamp")
    print("  - last_login: Last successful login")
    print()
    print("Roles:")
    print("  Admin: Full access (view all, delete, manage users, statistics)")
    print("  Analyst: Limited access (submit, view own, search own)")
    print()
    print("Security Notes:")
    print("  - NEVER store plain text passwords!")
    print("  - ALWAYS hash with bcrypt (password_hash library)")
    print("  - NEVER return hashed_password in API responses")
    print("  - Use JWT tokens for session management")
