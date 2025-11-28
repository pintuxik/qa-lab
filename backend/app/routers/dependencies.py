from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.services import AuthService, TaskService, UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# Service dependencies
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get UserService instance"""
    return UserService(db)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance"""
    return AuthService(db)


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """Dependency to get TaskService instance"""
    return TaskService(db)


# User authentication dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """
    Dependency to get current authenticated user

    Args:
        token: JWT token from request
        auth_service: Authentication service

    Returns:
        Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    return auth_service.get_current_user(token)
