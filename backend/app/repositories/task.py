from typing import List, Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.repositories import BaseRepository
from app.schemas import TaskCreate


class TaskRepository(BaseRepository[Task]):
    """Repository for Task-specific data access operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_id_and_owner(self, task_id: int, owner_id: int) -> Optional[Task]:
        """Get task by ID and owner ID for authorization checks."""
        stmt = select(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a specific owner with pagination."""
        stmt = select(Task).where(Task.owner_id == owner_id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_task(self, task_data: TaskCreate, owner_id: int) -> Task:
        """Create a new task from a Pydantic schema."""
        task = Task(**task_data.model_dump(), owner_id=owner_id)
        return await self.create(task)

    async def update_task(self, task: Task, update_data: dict) -> Task:
        """Update task with given data dictionary."""
        for field, value in update_data.items():
            setattr(task, field, value)
        return await self.update(task)

    async def delete_by_id_and_owner(self, task_id: int, owner_id: int) -> bool:
        """Delete task with single query. Returns True if deleted, False if not found.

        This optimized method performs DELETE with WHERE clause in a single database
        round-trip instead of fetch-then-delete pattern, significantly reducing latency
        and connection pool contention under high concurrency.
        """
        stmt = delete(Task).where(Task.id == task_id, Task.owner_id == owner_id)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount > 0
