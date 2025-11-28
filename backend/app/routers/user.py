"""User management router - handles user CRUD operations."""

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.config import settings
from app.models import User
from app.routers.dependencies import get_current_user, get_user_service
from app.schemas import TestCleanupRequest, UserCreate
from app.schemas import User as UserSchema
from app.services import UserService

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    Register a new user.

    Returns the created user with hashed password removed.
    """
    return user_service.register_user(user)


@router.get("/me", response_model=UserSchema)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.

    Requires authentication.
    """
    return current_user


@router.delete("/me")
def delete_current_user(
    current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)
):
    """
    Delete current authenticated user's account.

    Users can only delete their own account.
    """
    user_service.delete_user(current_user.id)
    return {"message": "User successfully deleted"}


@router.post("/test-cleanup")
def cleanup_test_users(
    request: TestCleanupRequest,
    x_test_api_key: str = Header(None, alias="X-Test-API-Key"),
    user_service: UserService = Depends(get_user_service),
):
    """
    Test-only endpoint to clean up test users.

    Requires TEST_MODE_ENABLED and valid API key.
    Used by automated tests to clean up test data.
    """
    # Check if test mode is enabled
    if not settings.TEST_MODE_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not available")

    # Validate API key
    if not x_test_api_key or x_test_api_key != settings.TEST_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing test API key")

    return user_service.cleanup_test_users(request)
