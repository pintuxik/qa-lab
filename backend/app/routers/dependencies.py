from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.services import AuthService, TaskService, UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_user_service(db: DbSessionDep) -> UserService:
    """Dependency to get UserService instance."""
    return UserService(db)


async def get_auth_service(db: DbSessionDep) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(db)


async def get_task_service(db: DbSessionDep) -> TaskService:
    """Dependency to get TaskService instance."""
    return TaskService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


async def get_current_user(auth_service: AuthServiceDep, token: str = Depends(oauth2_scheme)) -> User:
    """Dependency to get current authenticated user."""
    return await auth_service.get_current_user(token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
