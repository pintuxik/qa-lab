from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskService:
    """Service for task business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)

    async def create_task(self, task_data: TaskCreate, owner_id: int) -> Task:
        """
        Create a new task."""
        task = await self.task_repo.create_task(task_data, owner_id)
        await self.task_repo.commit()
        return task

    async def get_user_tasks(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get all tasks for a user with pagination."""
        return await self.task_repo.get_all_by_owner(owner_id, skip, limit)

    async def get_task(self, task_id: int, owner_id: int) -> Task:
        """Get a specific task with authorization check."""
        task = await self.task_repo.get_by_id_and_owner(task_id, owner_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    async def update_task(self, task_id: int, task_data: TaskUpdate, owner_id: int) -> Task:
        """Update a task with partial data."""
        task = await self.get_task(task_id, owner_id)
        update_data = task_data.model_dump(exclude_unset=True)
        updated_task = await self.task_repo.update_task(task, update_data)
        await self.task_repo.commit()
        return updated_task

    async def delete_task(self, task_id: int, owner_id: int) -> None:
        """Delete a task."""
        task = await self.get_task(task_id, owner_id)
        await self.task_repo.delete(task)
        await self.task_repo.commit()
