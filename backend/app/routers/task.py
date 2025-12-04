"""Task management router - handles task CRUD operations."""

from typing import List

from fastapi import APIRouter

from app.routers.dependencies import CurrentUserDep, TaskServiceDep
from app.schemas import Task as TaskSchema
from app.schemas import TaskCreate, TaskUpdate

router = APIRouter()


@router.get("/", response_model=List[TaskSchema])
async def get_tasks(
    current_user: CurrentUserDep,
    task_service: TaskServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get all tasks for the current user."""
    return await task_service.get_user_tasks(current_user.id, skip, limit)


@router.post("/", response_model=TaskSchema)
async def create_task(
    task: TaskCreate,
    current_user: CurrentUserDep,
    task_service: TaskServiceDep,
):
    """Create a new task."""
    return await task_service.create_task(task, current_user.id)


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: int,
    current_user: CurrentUserDep,
    task_service: TaskServiceDep,
):
    """Get a specific task."""
    return await task_service.get_task(task_id, current_user.id)


@router.put("/{task_id}", response_model=TaskSchema)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: CurrentUserDep,
    task_service: TaskServiceDep,
):
    """Update a task."""
    return await task_service.update_task(task_id, task_update, current_user.id)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: CurrentUserDep,
    task_service: TaskServiceDep,
):
    """Delete a task."""
    await task_service.delete_task(task_id, current_user.id)
    return {"message": "Task deleted successfully"}
