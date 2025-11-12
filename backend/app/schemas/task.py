from datetime import datetime
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TaskBase(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=100)]
    description: Optional[Annotated[str, Field(min_length=1, max_length=500)]] = None
    priority: Literal["low", "medium", "high"] = "medium"
    category: Optional[Annotated[str, Field(min_length=1, max_length=50)]] = None

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "title": "Complete project documentation",
                    "description": "Write comprehensive documentation for the new API endpoints",
                    "priority": "high",
                    "category": "documentation",
                }
            ]
        },
    )

    @field_validator("description", "category", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        """Convert empty strings to None."""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[Annotated[str, Field(min_length=1, max_length=100)]] = None
    description: Optional[Annotated[str, Field(min_length=1, max_length=500)]] = None
    is_completed: Optional[bool] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    category: Optional[Annotated[str, Field(min_length=1, max_length=50)]] = None

    @model_validator(mode="before")
    @classmethod
    def check_non_nullable_fields(cls, data):
        # If title is explicitly provided and is None, raise an error
        if isinstance(data, dict) and "title" in data and data["title"] is None:
            raise ValueError("title cannot be null")
        return data


class Task(TaskBase):
    id: int
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
