import pytest
from fastapi.testclient import TestClient
from main import app
from src.core.repository import TaskRepository
from src.core.repository import get_task_repository


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


def test_predict_high_priority(client):
    prediction_data = {
        "task_description": "Fix critical security vulnerability in authentication system"
    }
    response = client.post("/predict", json=prediction_data)

    assert response.status_code == 200
    data = response.json()
    assert data["task_description"] == prediction_data["task_description"]
    assert "predicted_priority" in data
    assert data["predicted_priority"] in ["high", "low"]
    assert "confidence" in data
    assert isinstance(data["confidence"], dict)


def test_predict_low_priority(client):
    prediction_data = {"task_description": "Update documentation for user guide"}
    response = client.post("/predict", json=prediction_data)

    assert response.status_code == 200
    data = response.json()
    assert data["task_description"] == prediction_data["task_description"]
    assert "predicted_priority" in data
    assert data["predicted_priority"] in ["high", "low"]


def test_predict_validation_error(client):
    prediction_data = {"task_description": ""}
    response = client.post("/predict", json=prediction_data)
    assert response.status_code == 422


def test_predict_missing_field(client):
    prediction_data = {}
    response = client.post("/predict", json=prediction_data)
    assert response.status_code == 422


def test_predict_various_tasks(client):
    test_cases = [
        "Implement new API endpoint for user management",
        "Clean up temporary files",
        "Optimize database queries",
        "Write unit tests for API",
        "Refactor old code",
    ]

    for task_description in test_cases:
        prediction_data = {"task_description": task_description}
        response = client.post("/predict", json=prediction_data)

        assert response.status_code == 200
        data = response.json()
        assert data["predicted_priority"] in ["high", "low"]
        assert "confidence" in data
        assert len(data["confidence"]) == 2
        assert "high" in data["confidence"]
        assert "low" in data["confidence"]
