"""User management router - handles user CRUD operations."""

from fastapi import APIRouter, Header, HTTPException, status

from app.core.config import settings
from app.routers.dependencies import CurrentUserDep, UserServiceDep
from app.schemas import TestCleanupRequest, UserCreate
from app.schemas import User as UserSchema

router = APIRouter()


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, user_service: UserServiceDep):
    """Register a new user."""
    return await user_service.register_user(user)


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: CurrentUserDep):
    """Get current authenticated user's profile."""
    return current_user


@router.delete("/me")
async def delete_current_user(current_user: CurrentUserDep, user_service: UserServiceDep):
    """Delete current authenticated user's account."""
    await user_service.delete_user(current_user.id)
    return {"message": "User successfully deleted"}


@router.post("/test-cleanup")
async def cleanup_test_users(
    request: TestCleanupRequest,
    user_service: UserServiceDep,
    x_test_api_key: str = Header(None, alias="X-Test-API-Key"),
):
    """
    Test-only endpoint to clean up test users.

    Requires TEST_MODE_ENABLED and valid API key.
    Used by automated tests to clean up test data.
    """
    if not settings.TEST_MODE_ENABLED:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not available")

    if not x_test_api_key or x_test_api_key != settings.TEST_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing test API key")

    return await user_service.cleanup_test_users(request)
