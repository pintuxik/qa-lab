"""Task management router - handles task CRUD operations."""

from typing import List

from fastapi import APIRouter, Depends

from app.models import User
from app.routers.dependencies import get_current_user, get_task_service
from app.schemas import Task as TaskSchema
from app.schemas import TaskCreate, TaskUpdate
from app.services import TaskService

router = APIRouter()


@router.get("/", response_model=List[TaskSchema])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Get all tasks for the current user"""
    return task_service.get_user_tasks(current_user.id, skip, limit)


@router.post("/", response_model=TaskSchema)
def create_task(
    task: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Create a new task"""
    return task_service.create_task(task, current_user.id)


@router.get("/{task_id}", response_model=TaskSchema)
def get_task(
    task_id: int, current_user: User = Depends(get_current_user), task_service: TaskService = Depends(get_task_service)
):
    """Get a specific task"""
    return task_service.get_task(task_id, current_user.id)


@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(get_task_service),
):
    """Update a task"""
    return task_service.update_task(task_id, task_update, current_user.id)


@router.delete("/{task_id}")
def delete_task(
    task_id: int, current_user: User = Depends(get_current_user), task_service: TaskService = Depends(get_task_service)
):
    """Delete a task"""
    task_service.delete_task(task_id, current_user.id)
    return {"message": "Task deleted successfully"}
