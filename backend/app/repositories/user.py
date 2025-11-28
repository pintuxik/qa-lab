from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.repositories import BaseRepository
from app.schemas import UserCreate


class UserRepository(BaseRepository[User]):
    """Repository for User data access"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user from schema"""
        user = User(**user_data.model_dump(exclude={"password"}), hashed_password=hashed_password)
        return self.create(user)

    def get_users_by_pattern(self, pattern: str) -> List[User]:
        """
        Get users by username pattern (glob-style wildcards)
        Converts glob pattern (* and ?) to SQL LIKE pattern (% and _)
        """
        sql_pattern = pattern.replace("*", "%").replace("?", "_")
        return self.db.query(User).filter(User.username.like(sql_pattern)).all()
