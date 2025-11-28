from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Task
from app.repositories import BaseRepository
from app.schemas import TaskCreate


class TaskRepository(BaseRepository[Task]):
    """Repository for Task data access"""

    def __init__(self, db: Session):
        super().__init__(Task, db)

    def get_by_id_and_owner(self, task_id: int, owner_id: int) -> Optional[Task]:
        """Get task by ID and owner ID"""
        return self.db.query(Task).filter(Task.id == task_id, Task.owner_id == owner_id).first()

    def get_all_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """Get all tasks for a specific owner with pagination"""
        return self.db.query(Task).filter(Task.owner_id == owner_id).offset(skip).limit(limit).all()

    def create_task(self, task_data: TaskCreate, owner_id: int) -> Task:
        """Create a new task from schema"""
        task = Task(**task_data.model_dump(), owner_id=owner_id)
        return self.create(task)

    def update_task(self, task: Task, update_data: dict) -> Task:
        """Update task with given data"""
        for field, value in update_data.items():
            setattr(task, field, value)
        return self.update(task)
