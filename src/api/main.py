from fastapi import FastAPI, HTTPException, Depends, Response, Request
from typing import List
from pydantic import BaseModel, field_validator
from src.core.models import TaskCreate, TaskUpdate, TaskResponse
from src.core.repository import get_task_repository, TaskRepository
from ml.predictor import PriorityPredictor


try:
    from src.tasks.celery_config import celery_app
    from src.tasks.tasks import fetch_users_from_api

    CELERY_ENABLED = True
except Exception:
    celery_app = None
    fetch_users_from_api = None
    CELERY_ENABLED = False

class PredictionRequest(BaseModel):
    task_description: str

    @field_validator('task_description')
    @classmethod
    def validate_task_description(cls, v):
        if not v or not v.strip():
            raise ValueError("Task description cannot be empty")
        return v

class PredictionResponse(BaseModel):
    task_description: str
    predicted_priority: str
    confidence: dict = None

app = FastAPI(
    title="Task Management API",
    description="REST API for managing a to-do list",
    version="1.0.0",
)

predictor = PriorityPredictor()


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
async def delete_task(
    task_id: int, repo: TaskRepository = Depends(get_task_repository)
):
    success = repo.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


if CELERY_ENABLED:

    @app.post("/api/fetch-users")
    async def trigger_fetch_users():
        task = fetch_users_from_api.delay()
        return {
            "task_id": task.id,
            "status": "Task started",
            "message": "User data fetch task has been queued",
        }


if CELERY_ENABLED:

    @app.get("/api/task-status/{task_id}")
    async def get_task_status(task_id: str):
        task = celery_app.AsyncResult(task_id)

        if task.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": "Task is waiting to be processed",
            }
        elif task.state == "SUCCESS":
            response = {"task_id": task_id, "state": task.state, "result": task.result}
        else:
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": (
                    task.info.get("message", "Unknown status")
                    if task.info
                    else "Unknown status"
                ),
            }

        return response


if CELERY_ENABLED:

    @app.get("/api/tasks/active")
    async def get_active_tasks():
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()

        if active_tasks is None:
            return {"message": "No Celery workers are currently running"}

        return {"active_tasks": active_tasks}


@app.post("/predict", response_model=PredictionResponse)
async def predict_priority(request: PredictionRequest):
    prediction = predictor.predict(request.task_description)
    confidence = predictor.predict_proba(request.task_description)

    return PredictionResponse(
        task_description=request.task_description,
        predicted_priority=prediction,
        confidence=confidence
    )
