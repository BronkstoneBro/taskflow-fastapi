from fastapi import FastAPI, HTTPException, Depends, Response, Request
from typing import List
from core.models import TaskCreate, TaskUpdate, TaskResponse
from core.repository import get_task_repository, TaskRepository

app = FastAPI(
    title="Task Management API",
    description="REST API for managing a to-do list",
    version="1.0.0",
)


@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(repo: TaskRepository = Depends(get_task_repository)):
    return repo.get_all_tasks()


@app.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    response: Response,
    repo: TaskRepository = Depends(get_task_repository),
):
    task = repo.create_task(task_data)
    response.headers["Location"] = str(request.url_for("get_task", task_id=task.id))
    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, repo: TaskRepository = Depends(get_task_repository)):
    task = repo.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    repo: TaskRepository = Depends(get_task_repository),
):
    task = repo.update_task(task_id, task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int, repo: TaskRepository = Depends(get_task_repository)):
    success = repo.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
