"""
Authentication API Routes
=========================
FastAPI routes for user authentication and registration.

Endpoints:
- POST /auth/register - Create new user account
- POST /auth/login - Login and get JWT token
- GET /auth/me - Get current user info
- POST /auth/refresh - Refresh JWT token (future)

Demonstrates:
- FastAPI route handlers
- Request/response models with Pydantic
- JWT token generation
- Password hashing
- Database operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth.jwt import hash_password, verify_password, create_token_for_user
from auth.dependencies import get_current_user

# Note: UserDB and get_db are imported inside functions to avoid circular imports
# They are defined in main.py

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# Request/Response Models
# ============================================================================

class UserRegisterRequest(BaseModel):
    """Request model for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    # Note: role is always set to "analyst" - admin accounts must be created via database migration

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123"
            }
        }


class UserLoginRequest(BaseModel):
    """Request model for user login"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class TokenResponse(BaseModel):
    """Response model for successful authentication"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    user: dict = Field(..., description="User information")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "role": "admin",
                    "is_active": True
                }
            }
        }


class UserResponse(BaseModel):
    """Response model for user information"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "analyst",
                "is_active": True,
                "created_at": "2024-01-15T10:30:00",
                "last_login": "2024-01-20T14:25:00"
            }
        }


# ============================================================================
# Authentication Routes
# ============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user account.

    Creates a new user with hashed password and returns JWT token.

    Args:
        user_data: User registration information

    Returns:
        TokenResponse with access token and user info

    Raises:
        400: Username or email already exists
        422: Invalid input data (validation error)

    Example:
        POST /auth/register
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "secure_password"
        }

        Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "user": {"username": "john_doe", "role": "analyst", ...}
        }

    Note:
        All new registrations are created as "analyst" role.
        Admin accounts must be created via database migration.
    """
    # Import here to avoid circular dependency
    from main import UserDB, SessionLocal

    # Create database session
    db = SessionLocal()
    try:
        # Force role to 'analyst' - admin accounts are created via migration only
        # This simplifies the college project by having only one admin
        user_role = "analyst"

        # Check if username already exists
        existing_user = db.query(UserDB).filter(UserDB.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        existing_email = db.query(UserDB).filter(UserDB.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = hash_password(user_data.password)

        # Create user in database
        new_user = UserDB(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_role,  # Always "analyst"
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create JWT token
        token = create_token_for_user(
            username=new_user.username,
            role=new_user.role,
            user_id=new_user.id
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=new_user.to_dict()
        )
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLoginRequest):
    """
    Login with username and password.

    Validates credentials and returns JWT token on success.

    Args:
        credentials: Username and password

    Returns:
        TokenResponse with access token and user info

    Raises:
        401: Invalid username or password
        403: User account is disabled

    Example:
        POST /auth/login
        {
            "username": "admin",
            "password": "admin123"
        }

        Response:
        {
            "access_token": "eyJhbGc...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "admin",
                "role": "admin",
                ...
            }
        }
    """
    # First, check for hardcoded demo accounts (for backwards compatibility)
    if credentials.username == "admin" and credentials.password == "admin123":
        user_dict = {
            "id": 1,
            "username": "admin",
            "email": "admin@fraud-detection.local",
            "role": "admin",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00",
            "last_login": datetime.utcnow().isoformat()
        }

        token = create_token_for_user(username="admin", role="admin", user_id=1)
        return TokenResponse(access_token=token, token_type="bearer", user=user_dict)

    if credentials.username == "analyst" and credentials.password == "analyst123":
        user_dict = {
            "id": 2,
            "username": "analyst",
            "email": "analyst@fraud-detection.local",
            "role": "analyst",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00",
            "last_login": datetime.utcnow().isoformat()
        }

        token = create_token_for_user(username="analyst", role="analyst", user_id=2)
        return TokenResponse(access_token=token, token_type="bearer", user=user_dict)

    # Import here to avoid circular dependency
    from main import UserDB, SessionLocal

    # Create database session
    db = SessionLocal()
    try:
        # Check database for registered users
        user = db.query(UserDB).filter(UserDB.username == credentials.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
            )

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login timestamp
        user.last_login = datetime.utcnow()
        db.commit()

        # Create JWT token
        token = create_token_for_user(
            username=user.username,
            role=user.role,
            user_id=user.id
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user.to_dict()
        )
    finally:
        db.close()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.

    Args:
        current_user: Current user from JWT token (injected by dependency)

    Returns:
        UserResponse with user information

    Raises:
        401: Invalid or expired token

    Example:
        GET /auth/me
        Authorization: Bearer eyJhbGc...

        Response:
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "is_active": true
        }
    """
    # In real implementation, fetch full user from database
    # user = db.query(UserDB).filter(UserDB.id == current_user['user_id']).first()

    # For now, return data from token
    return UserResponse(
        id=current_user.get("user_id", 1),
        username=current_user["username"],
        email=f"{current_user['username']}@fraud-detection.local",
        role=current_user["role"],
        is_active=True,
        created_at=None,
        last_login=None
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout (invalidate token).

    Note: With JWT, we can't truly invalidate tokens server-side unless we maintain
    a blacklist. For now, this is a placeholder that confirms the token is valid.
    Client should delete the token on their end.

    Args:
        current_user: Current user (ensures token is valid)

    Returns:
        Success message

    Example:
        POST /auth/logout
        Authorization: Bearer eyJhbGc...

        Response:
        {
            "message": "Successfully logged out"
        }
    """
    # In a real implementation with token blacklist:
    # - Add token to Redis blacklist with expiration = token's remaining lifetime
    # - Check blacklist in get_current_user dependency

    return {
        "message": "Successfully logged out",
        "username": current_user["username"]
    }


# ============================================================================
# Admin Routes
# ============================================================================

@router.get("/admin/users", response_model=list[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """
    Get all users (admin only).

    Returns a list of all registered users.

    Args:
        current_user: Current user from JWT token

    Returns:
        List of UserResponse objects

    Raises:
        403: User is not an admin

    Example:
        GET /auth/admin/users
        Authorization: Bearer eyJhbGc...

        Response:
        [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "is_active": true,
                "created_at": "2024-01-01T00:00:00",
                "last_login": "2024-01-20T14:25:00"
            },
            ...
        ]
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )

    # Import here to avoid circular dependency
    from main import UserDB, SessionLocal

    db = SessionLocal()
    try:
        # Fetch all users from database
        users = db.query(UserDB).all()

        # Convert to response format
        return [
            UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at.isoformat() if user.created_at else None,
                last_login=user.last_login.isoformat() if user.last_login else None
            )
            for user in users
        ]
    finally:
        db.close()


class UpdateUserStatusRequest(BaseModel):
    """Request model for updating user status"""
    is_active: bool = Field(..., description="New active status")


class UpdateUserRoleRequest(BaseModel):
    """Request model for updating user role"""
    role: str = Field(..., description="New role: 'admin' or 'analyst'")


@router.patch("/admin/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: UpdateUserStatusRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user active status (admin only).

    Args:
        user_id: ID of user to update
        status_data: New status
        current_user: Current user from JWT token

    Returns:
        Updated user information

    Raises:
        403: User is not an admin
        404: User not found
        400: Cannot disable own account
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )

    from main import UserDB, SessionLocal

    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent disabling own account
        if user.id == current_user.get("user_id") and not status_data.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disable your own account"
            )

        user.is_active = status_data.is_active
        db.commit()
        db.refresh(user)

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    finally:
        db.close()


@router.patch("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: UpdateUserRoleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update user role (admin only).

    Args:
        user_id: ID of user to update
        role_data: New role
        current_user: Current user from JWT token

    Returns:
        Updated user information

    Raises:
        403: User is not an admin
        404: User not found
        400: Cannot change own role or invalid role
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )

    # Validate role
    if role_data.role not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin' or 'analyst'"
        )

    from main import UserDB, SessionLocal

    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent changing own role
        if user.id == current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )

        user.role = role_data.role
        db.commit()
        db.refresh(user)

        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            last_login=user.last_login.isoformat() if user.last_login else None
        )
    finally:
        db.close()


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete user (admin only).

    Args:
        user_id: ID of user to delete
        current_user: Current user from JWT token

    Returns:
        Success message

    Raises:
        403: User is not an admin
        404: User not found
        400: Cannot delete own account
    """
    # Check if user is admin
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access this endpoint"
        )

    from main import UserDB, SessionLocal

    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Prevent deleting own account
        if user.id == current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        db.delete(user)
        db.commit()

        return {"message": "User deleted successfully", "username": user.username}
    finally:
        db.close()


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def auth_health_check():
    """
    Health check endpoint for authentication service.

    Returns:
        Service status
    """
    return {
        "service": "authentication",
        "status": "healthy",
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "me": "GET /auth/me",
            "logout": "POST /auth/logout"
        }
    }


# Example usage documentation
if __name__ == "__main__":
    print("Authentication Routes Documentation")
    print("=" * 60)
    print()
    print("Available Endpoints:")
    print()
    print("1. POST /auth/register")
    print("   - Create new user account (always as 'analyst' role)")
    print("   - Body: {username, email, password}")
    print("   - Returns: JWT token + user info")
    print()
    print("2. POST /auth/login")
    print("   - Login with credentials")
    print("   - Body: {username, password}")
    print("   - Returns: JWT token + user info")
    print()
    print("3. GET /auth/me")
    print("   - Get current user info")
    print("   - Requires: Authorization header with JWT")
    print("   - Returns: User information")
    print()
    print("4. POST /auth/logout")
    print("   - Logout (client should delete token)")
    print("   - Requires: Authorization header with JWT")
    print("   - Returns: Success message")
    print()
    print("5. GET /auth/health")
    print("   - Health check")
    print("   - No authentication required")
    print("   - Returns: Service status")
    print()
    print("Test Credentials (hardcoded for now):")
    print("  Username: admin")
    print("  Password: admin123")
