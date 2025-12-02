"""Security utilities for password hashing and OAuth2 configuration.

This module provides:
- Password hashing and verification using bcrypt
- OAuth2 password bearer scheme for FastAPI

Note: Authentication logic (user authentication, token generation, current user retrieval)
has been moved to AuthService in app/services/auth.py
"""

import asyncio

import bcrypt
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Runs bcrypt.checkpw in a thread pool to avoid blocking the event loop.
    bcrypt is CPU-intensive (~100-200ms per call) and must not block async operations.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """

    def _verify():
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    return await asyncio.to_thread(_verify)


async def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Runs bcrypt.hashpw in a thread pool to avoid blocking the event loop.
    bcrypt is CPU-intensive (~100-200ms per call) and must not block async operations.

    Args:
        password: The plain text password to hash

    Returns:
        The bcrypt hashed password as a string
    """

    def _hash():
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    return await asyncio.to_thread(_hash)
