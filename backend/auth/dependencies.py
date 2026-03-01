"""
FastAPI Authentication Dependencies
====================================
Dependency injection functions for protecting API endpoints.

Demonstrates:
- FastAPI dependency injection
- JWT token validation from HTTP headers
- Role-based access control (RBAC)
- Reusable authentication logic

Usage in routes:
    @app.get("/protected")
    async def protected_route(current_user: UserDB = Depends(get_current_user)):
        # current_user is automatically validated from JWT token
        return {"username": current_user.username}

    @app.delete("/admin-only")
    async def admin_route(current_user: UserDB = Depends(require_admin)):
        # Only users with role='admin' can access this
        return {"message": "Admin access granted"}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from auth.jwt import verify_token
from exceptions import (
    TokenExpiredException,
    InvalidCredentialsException,
    InsufficientPermissionsException
)

# HTTP Bearer scheme for JWT tokens
# This tells FastAPI to expect: Authorization: Bearer <token>
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.

    This function:
    1. Extracts JWT token from Authorization header
    2. Verifies token signature and expiration
    3. Returns user information from token

    Args:
        credentials: HTTP Bearer credentials (automatically extracted by FastAPI)
        db: Database session (optional, for future user lookup)

    Returns:
        Dictionary with user information from token: {
            "username": str,
            "role": str,
            "user_id": Optional[int]
        }

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 403: If user account is disabled

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"message": f"Hello {user['username']}"}
    """
    # Extract token from credentials
    token = credentials.credentials

    try:
        # Verify and decode token
        payload = verify_token(token)

        # Extract user information from token
        username = payload.get("sub")
        role = payload.get("role", "analyst")
        user_id = payload.get("user_id")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Return user info
        return {
            "username": username,
            "role": role,
            "user_id": user_id
        }

    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require admin role.

    This function:
    1. Gets current user (via get_current_user dependency)
    2. Checks if user has admin role
    3. Raises 403 Forbidden if user is not admin

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User dictionary (same as get_current_user)

    Raises:
        HTTPException 403: If user does not have admin role

    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: int,
            admin: dict = Depends(require_admin)
        ):
            # Only admins can access this endpoint
            return {"message": f"Admin {admin['username']} deleting user {user_id}"}
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Admin role required. Your role: {current_user.get('role')}"
        )

    return current_user


def require_analyst_or_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to require analyst or admin role (any authenticated user).

    This is essentially the same as get_current_user, but more explicit.
    Use this when you want to make it clear that the endpoint requires authentication.

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        User dictionary

    Usage:
        @app.get("/api/transactions/my")
        async def get_my_transactions(
            user: dict = Depends(require_analyst_or_admin)
        ):
            # Both analysts and admins can access
            return {"transactions": get_user_transactions(user['user_id'])}
    """
    # Any authenticated user is allowed (analyst or admin)
    return current_user


def optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Dependency for optional authentication.

    Returns user if token is provided and valid, None otherwise.
    Does NOT raise error if no token provided.

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        User dictionary if authenticated, None if not

    Usage:
        @app.get("/api/public-or-private")
        async def mixed_endpoint(user: Optional[dict] = Depends(optional_user)):
            if user:
                return {"message": f"Authenticated as {user['username']}"}
            else:
                return {"message": "Public access"}
    """
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token)
        return {
            "username": payload.get("sub"),
            "role": payload.get("role", "analyst"),
            "user_id": payload.get("user_id")
        }
    except Exception:
        # Invalid token - return None (no user)
        return None


# Helper functions for use in route handlers

def check_permission(user: dict, required_role: str) -> bool:
    """
    Check if user has required role.

    Args:
        user: User dictionary from dependency
        required_role: Required role ('admin' or 'analyst')

    Returns:
        True if user has required role or higher

    Example:
        if not check_permission(current_user, "admin"):
            raise HTTPException(403, "Admin required")
    """
    if required_role == "admin":
        return user.get("role") == "admin"
    elif required_role == "analyst":
        return user.get("role") in ["admin", "analyst"]
    return False


def is_admin(user: dict) -> bool:
    """
    Check if user is admin.

    Args:
        user: User dictionary

    Returns:
        True if user has admin role

    Example:
        if is_admin(current_user):
            # Show admin features
    """
    return user.get("role") == "admin"


def is_owner_or_admin(user: dict, resource_owner_id: int) -> bool:
    """
    Check if user owns resource or is admin.

    Useful for endpoints where users can access their own resources,
    or admins can access any resource.

    Args:
        user: Current user
        resource_owner_id: ID of user who owns the resource

    Returns:
        True if user owns resource or is admin

    Example:
        transaction = get_transaction(transaction_id)
        if not is_owner_or_admin(current_user, transaction.user_id):
            raise HTTPException(403, "Can only access your own transactions")
    """
    if is_admin(user):
        return True
    return user.get("user_id") == resource_owner_id


# Example usage
if __name__ == "__main__":
    print("FastAPI Authentication Dependencies")
    print("=" * 60)
    print()
    print("Available dependencies:")
    print()
    print("1. get_current_user:")
    print("   - Validates JWT token from Authorization header")
    print("   - Returns user info: {username, role, user_id}")
    print("   - Raises 401 if token invalid/expired")
    print()
    print("2. require_admin:")
    print("   - Same as get_current_user but requires admin role")
    print("   - Raises 403 if user is not admin")
    print()
    print("3. require_analyst_or_admin:")
    print("   - Requires any authenticated user")
    print("   - More explicit than get_current_user")
    print()
    print("4. optional_user:")
    print("   - Returns user if token provided and valid")
    print("   - Returns None if no token (no error)")
    print()
    print("Usage in routes:")
    print()
    print("  @app.get('/protected')")
    print("  async def protected(user: dict = Depends(get_current_user)):")
    print("      return {'user': user['username']}")
    print()
    print("  @app.delete('/admin-only')")
    print("  async def admin_only(admin: dict = Depends(require_admin)):")
    print("      return {'message': 'Admin access granted'}")
