from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import User
from app.repositories import UserRepository
from app.schemas import TestCleanupRequest, UserCreate


class UserService:
    """Service for user business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user with validation

        Args:
            user_data: User registration data

        Returns:
            Created user

        Raises:
            HTTPException: If email or username already exists
        """
        # Check if email already exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if username already exists
        existing_user = self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        # Create the user
        user = self.user_repo.create_user(user_data, hashed_password)

        # Commit the transaction
        self.user_repo.commit()

        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.user_repo.get_by_username(username)

    def delete_user(self, user_id: int) -> None:
        """
        Delete a user by ID

        Args:
            user_id: ID of the user to delete

        Raises:
            HTTPException: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.user_repo.delete(user)
        self.user_repo.commit()

    def cleanup_test_users(self, request: TestCleanupRequest) -> dict:
        """
        Clean up test users by IDs or username patterns

        Args:
            request: Test cleanup request with user_ids and/or username_patterns

        Returns:
            Dictionary with deletion count and deleted users info
        """
        deleted_count = 0
        deleted_users = []

        # Delete users by IDs
        if request.user_ids:
            for user_id in request.user_ids:
                user = self.user_repo.get_by_id(user_id)
                if user:
                    deleted_users.append({"id": user.id, "username": user.username})
                    self.user_repo.delete(user)
                    deleted_count += 1

        # Delete users by username patterns
        if request.username_patterns:
            for pattern in request.username_patterns:
                users = self.user_repo.get_users_by_pattern(pattern)
                for user in users:
                    # Avoid double deletion if already deleted by ID
                    if user.id not in [u["id"] for u in deleted_users]:
                        deleted_users.append({"id": user.id, "username": user.username})
                        self.user_repo.delete(user)
                        deleted_count += 1

        # Commit all deletions
        self.user_repo.commit()

        return {
            "message": f"Successfully deleted {deleted_count} test user(s)",
            "deleted_count": deleted_count,
            "deleted_users": deleted_users,
        }
