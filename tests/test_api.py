import pytest
from fastapi.testclient import TestClient
from main import app
from core.repository import TaskRepository
from core.repository import get_task_repository


@pytest.fixture
def client():
    repo = TaskRepository()

    def override_repo():
        return repo

    app.dependency_overrides[get_task_repository] = override_repo
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_task_repository, None)


@pytest.fixture(autouse=True)
def _no_implicit_cleanup():
    yield


def test_get_empty_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
    }
    response = client.post("/tasks", json=task_data)

    assert response.status_code == 201
    assert response.headers.get("Location", "").endswith("/tasks/1")
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["completed"] == False
    assert "created_at" in data


def test_create_task_minimal(client):
    task_data = {"title": "Minimal Task"}
    response = client.post("/tasks", json=task_data)

    assert response.status_code == 201
    location = response.headers.get("Location")
    assert location is not None and "/tasks/" in location
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["description"] is None
    assert data["completed"] == False


def test_create_task_validation_error(client):
    task_data = {"title": ""}
    response = client.post("/tasks", json=task_data)
    assert response.status_code == 422


def test_get_all_tasks(client):
    client.post("/tasks", json={"title": "Task 1"})
    client.post("/tasks", json={"title": "Task 2"})

    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Task 1"
    assert data[1]["title"] == "Task 2"


def test_get_task_by_id(client):
    create_response = client.post("/tasks", json={"title": "Test Task"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"


def test_get_task_not_found(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_update_task(client):
    create_response = client.post("/tasks", json={"title": "Original Task"})
    task_id = create_response.json()["id"]

    update_data = {
        "title": "Updated Task",
        "description": "Updated Description",
        "completed": True,
    }
    response = client.put(f"/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated Description"
    assert data["completed"] == True


def test_update_task_partial(client):
    create_response = client.post("/tasks", json={"title": "Original Task"})
    task_id = create_response.json()["id"]

    update_data = {"completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Original Task"
    assert data["completed"] == True


def test_update_task_not_found(client):
    update_data = {"title": "Updated Task"}
    response = client.put("/tasks/999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_task(client):
    create_response = client.post("/tasks", json={"title": "Task to Delete"})
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_task_workflow(client):
    task_data = {"title": "Workflow Task", "description": "Test workflow"}

    create_response = client.post("/tasks", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["completed"] == False

    update_response = client.put(f"/tasks/{task_id}", json={"completed": True})
    assert update_response.status_code == 200
    assert update_response.json()["completed"] == True

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    final_get_response = client.get(f"/tasks/{task_id}")
    assert final_get_response.status_code == 404
