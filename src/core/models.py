from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Model for creating new tasks."""

    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: bool = Field(False, description="Task completion status")


class TaskUpdate(BaseModel):
    """Model for updating existing tasks. All fields are optional."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Task title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Task description"
    )
    completed: Optional[bool] = Field(None, description="Task completion status")


class Task(BaseModel):
    """Complete task model with ID and timestamps."""

    id: int = Field(..., description="Task unique identifier")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(False, description="Task completion status")
    created_at: datetime = Field(..., description="Task creation timestamp")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TaskResponse(Task):
    """API response model for tasks."""

    pass
