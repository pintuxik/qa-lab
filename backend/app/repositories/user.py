from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import BaseRepository
from app.schemas import UserCreate


class UserRepository(BaseRepository[User]):
    """Repository for User-specific data access operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user from a Pydantic schema."""
        user = User(**user_data.model_dump(exclude={"password"}), hashed_password=hashed_password)
        return await self.create(user)

    async def get_users_by_pattern(self, pattern: str) -> List[User]:
        """
        Get users by username pattern using glob-style wildcards."""
        sql_pattern = pattern.replace("*", "%").replace("?", "_")
        stmt = select(User).where(User.username.like(sql_pattern))
        result = await self.db.execute(stmt)
        return result.scalars().all()
