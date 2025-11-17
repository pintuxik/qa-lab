import re
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    username: Annotated[str, Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")]

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "john_doe",
                }
            ]
        },
    )


class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8, max_length=128)]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "email": "newuser@example.com",
                    "username": "new_user",
                    "password": "SecurePass123!",
                }
            ]
        }
    )

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password complexity requirements."""
        errors = []
        if not re.search(r"[a-z]", v):
            errors.append("lowercase letter")
        if not re.search(r"[A-Z]", v):
            errors.append("uppercase letter")
        if not re.search(r"\d", v):
            errors.append("digit")
        if not re.search(r"[@$!%*?&]", v):
            errors.append("special character (@$!%*?&)")

        if errors:
            raise ValueError(f"Password must contain at least one: {', '.join(errors)}")
        return v


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
