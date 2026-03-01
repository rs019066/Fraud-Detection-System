"""
JWT Token Management and Password Hashing
==========================================
Handles JWT token creation/verification and secure password hashing.

Security Best Practices:
- Uses bcrypt for password hashing (slow hashing = resistant to brute force)
- JWT tokens with expiration (prevents token replay attacks)
- HS256 algorithm for token signing
- Secrets stored in Config (environment variables in production)

Dependencies:
- python-jose[cryptography]: JWT token handling
- passlib[bcrypt]: Secure password hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import Config
from exceptions import TokenExpiredException, InvalidCredentialsException


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Bcrypt advantages:
    - Slow hashing algorithm (prevents brute force)
    - Automatic salt generation
    - Adaptive cost factor (can increase rounds as computers get faster)

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt-hashed password (safe to store in database)

    Example:
        >>> hashed = hash_password("my_secret_password")
        >>> print(hashed)
        $2b$12$... (60 character bcrypt hash)
    """
    # Bcrypt works with bytes
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.

    Args:
        plain_password: Plain text password from user login
        hashed_password: Bcrypt hash from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("correct_password")
        >>> verify_password("correct_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    JWT Token Structure:
    {
        "sub": "username",       # Subject (who the token is for)
        "role": "admin",         # User role for authorization
        "exp": 1234567890,       # Expiration timestamp
        "iat": 1234567890        # Issued at timestamp
    }

    Args:
        data: Dictionary of claims to include in token (e.g., {"sub": "username", "role": "admin"})
        expires_delta: How long until token expires (default: Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token({"sub": "admin", "role": "admin"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow()  # Issued at time
    })

    # Encode token with secret key
    encoded_jwt = jwt.encode(
        to_encode,
        Config.SECRET_KEY,
        algorithm=Config.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        Decoded token payload (dictionary with claims)

    Raises:
        TokenExpiredException: If token has expired
        InvalidCredentialsException: If token is invalid/malformed

    Example:
        >>> token = create_access_token({"sub": "admin", "role": "admin"})
        >>> payload = verify_token(token)
        >>> print(payload["sub"])
        admin
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=[Config.ALGORITHM]
        )

        # Check if token has required claims
        if payload.get("sub") is None:
            raise InvalidCredentialsException("Token missing 'sub' claim")

        return payload

    except jwt.ExpiredSignatureError:
        # Token has expired
        raise TokenExpiredException()

    except JWTError as e:
        # Invalid token (bad signature, malformed, etc.)
        raise InvalidCredentialsException(f"Invalid token: {str(e)}")


def decode_token_unsafe(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT token WITHOUT verification (for debugging only).

    WARNING: Never use this for authentication! Only for debugging/logging.

    Args:
        token: JWT token to decode

    Returns:
        Decoded payload or None if decode fails

    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = decode_token_unsafe(token)
        >>> print(payload)  # Shows token contents without verifying signature
    """
    try:
        # Decode without verification (options={"verify_signature": False})
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return payload
    except Exception:
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get expiration time from a token (without full verification).

    Useful for checking how much time is left before token expires.

    Args:
        token: JWT token

    Returns:
        Expiration datetime or None if token is invalid

    Example:
        >>> token = create_access_token({"sub": "user"})
        >>> exp_time = get_token_expiration(token)
        >>> print(f"Token expires at: {exp_time}")
    """
    payload = decode_token_unsafe(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def create_token_for_user(username: str, role: str, user_id: Optional[int] = None) -> str:
    """
    Convenience function to create a token for a user.

    Args:
        username: Username to include in token
        role: User role ('admin' or 'analyst')
        user_id: Optional user ID to include

    Returns:
        JWT access token

    Example:
        >>> token = create_token_for_user("admin", "admin", user_id=1)
        >>> # Token includes: sub=admin, role=admin, user_id=1, exp=...
    """
    token_data = {
        "sub": username,
        "role": role
    }

    if user_id is not None:
        token_data["user_id"] = user_id

    return create_access_token(token_data)


# Example usage and testing
if __name__ == "__main__":
    print("JWT Token Management Demo")
    print("=" * 60)
    print()

    # Password hashing demo
    print("1. Password Hashing:")
    password = "my_secure_password_123"
    hashed = hash_password(password)
    print(f"   Plain text: {password}")
    print(f"   Hashed: {hashed}")
    print(f"   Verify correct: {verify_password(password, hashed)}")
    print(f"   Verify wrong: {verify_password('wrong_password', hashed)}")
    print()

    # Token creation demo
    print("2. JWT Token Creation:")
    token = create_token_for_user("admin", "admin", user_id=1)
    print(f"   Token: {token[:50]}...")
    print()

    # Token verification demo
    print("3. JWT Token Verification:")
    try:
        payload = verify_token(token)
        print(f"   Valid token!")
        print(f"   Username: {payload['sub']}")
        print(f"   Role: {payload['role']}")
        print(f"   User ID: {payload.get('user_id')}")
        print(f"   Expires: {datetime.fromtimestamp(payload['exp'])}")
    except Exception as e:
        print(f"   Error: {e}")
    print()

    # Token expiration demo
    print("4. Token Expiration:")
    exp_time = get_token_expiration(token)
    time_left = exp_time - datetime.utcnow()
    print(f"   Expires at: {exp_time}")
    print(f"   Time left: {time_left.total_seconds() / 60:.1f} minutes")
    print()

    # Short-lived token demo
    print("5. Short-Lived Token (expires in 1 second):")
    short_token = create_access_token(
        {"sub": "test"},
        expires_delta=timedelta(seconds=1)
    )
    print(f"   Created short-lived token")

    import time
    print("   Waiting 2 seconds...")
    time.sleep(2)

    try:
        verify_token(short_token)
        print("   Token still valid (unexpected!)")
    except TokenExpiredException:
        print("   ✅ Token expired as expected")
    except Exception as e:
        print(f"   Error: {e}")
