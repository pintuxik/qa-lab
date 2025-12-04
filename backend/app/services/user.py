from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models import User
from app.repositories import UserRepository
from app.schemas import TestCleanupRequest, UserCreate


class UserService:
    """Service for user business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user with validation."""
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_password = await get_password_hash(user_data.password)
        user = await self.user_repo.create_user(user_data, hashed_password)
        await self.user_repo.commit()
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repo.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.user_repo.get_by_username(username)

    async def delete_user(self, user_id: int) -> None:
        """Delete a user by ID."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await self.user_repo.delete(user)
        await self.user_repo.commit()

    async def cleanup_test_users(self, request: TestCleanupRequest) -> dict:
        """Clean up test users by IDs or username patterns."""
        deleted_count = 0
        deleted_users = []

        if request.user_ids:
            for user_id in request.user_ids:
                user = await self.user_repo.get_by_id(user_id)
                if user:
                    deleted_users.append({"id": user.id, "username": user.username})
                    await self.user_repo.delete(user)
                    deleted_count += 1

        if request.username_patterns:
            for pattern in request.username_patterns:
                users = await self.user_repo.get_users_by_pattern(pattern)
                for user in users:
                    if user.id not in [u["id"] for u in deleted_users]:
                        deleted_users.append({"id": user.id, "username": user.username})
                        await self.user_repo.delete(user)
                        deleted_count += 1

        await self.user_repo.commit()
        return {
            "message": f"Successfully deleted {deleted_count} test user(s)",
            "deleted_count": deleted_count,
            "deleted_users": deleted_users,
        }
