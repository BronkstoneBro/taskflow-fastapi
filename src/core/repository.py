from datetime import datetime
from typing import Dict, List, Optional
from src.core.models import Task, TaskCreate, TaskUpdate


class TaskRepository:
    """In-memory repository for task CRUD operations."""

    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id: int = 1

    def create_task(self, task_data: TaskCreate) -> Task:
        """Create new task with auto-generated ID."""
        task = Task(
            id=self._next_id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            created_at=datetime.now(),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks currently stored in memory."""
        return list(self._tasks.values())

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Return a task by ID or None if not found."""
        return self._tasks.get(task_id)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """Apply partial updates to a task and return it, or None if missing."""
        task = self._tasks.get(task_id)
        if not task:
            return None

        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        return task

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID. Return True if deleted, False if not found."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def task_exists(self, task_id: int) -> bool:
        return task_id in self._tasks


task_repository = TaskRepository()


def get_task_repository() -> "TaskRepository":
    """FastAPI dependency provider for TaskRepository.

    Returns the default in-memory singleton. Tests can override this dependency
    to inject a fresh repository instance per test.
    """
    return task_repository
