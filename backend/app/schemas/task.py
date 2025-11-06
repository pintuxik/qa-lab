from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    category: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None
    category: Optional[str] = None

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
