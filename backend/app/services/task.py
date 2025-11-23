from typing import List

from app.models import Task
from app.repositories import TaskRepository
from app.schemas import TaskCreate, TaskUpdate
from fastapi import HTTPException
from sqlalchemy.orm import Session


class TaskService:
    """Service for task business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.task_repo = TaskRepository(db)

    def create_task(self, task_data: TaskCreate, owner_id: int) -> Task:
        """
        Create a new task

        Args:
            task_data: Task creation data
            owner_id: ID of the task owner

        Returns:
            Created task
        """
        task = self.task_repo.create_task(task_data, owner_id)
        self.task_repo.commit()
        return task

    def get_user_tasks(self, owner_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Get all tasks for a user

        Args:
            owner_id: ID of the task owner
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of tasks
        """
        return self.task_repo.get_all_by_owner(owner_id, skip, limit)

    def get_task(self, task_id: int, owner_id: int) -> Task:
        """
        Get a specific task

        Args:
            task_id: ID of the task
            owner_id: ID of the task owner

        Returns:
            Task

        Raises:
            HTTPException: If task not found
        """
        task = self.task_repo.get_by_id_and_owner(task_id, owner_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def update_task(self, task_id: int, task_data: TaskUpdate, owner_id: int) -> Task:
        """
        Update a task

        Args:
            task_id: ID of the task
            task_data: Task update data
            owner_id: ID of the task owner

        Returns:
            Updated task

        Raises:
            HTTPException: If task not found
        """
        task = self.get_task(task_id, owner_id)

        # Get only the fields that were provided
        update_data = task_data.model_dump(exclude_unset=True)

        # Update the task
        updated_task = self.task_repo.update_task(task, update_data)
        self.task_repo.commit()

        return updated_task

    def delete_task(self, task_id: int, owner_id: int) -> None:
        """
        Delete a task

        Args:
            task_id: ID of the task
            owner_id: ID of the task owner

        Raises:
            HTTPException: If task not found
        """
        task = self.get_task(task_id, owner_id)
        self.task_repo.delete(task)
        self.task_repo.commit()
