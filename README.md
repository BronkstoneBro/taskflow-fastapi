# TaskFlow FastAPI

Small REST API for managing a to‑do list with **machine learning integration** for task priority prediction. Built with FastAPI, stores data in‑memory, and is covered by unit tests. Features ML-powered priority classification, optional Celery background processing, and full Docker setup.

## Features
- Task CRUD: GET/POST/PUT/DELETE `/tasks`
- **ML Integration**: Task priority prediction via `/predict` endpoint
- Request validation with Pydantic
- In‑memory storage (`dict`/`list`)
- Unit tests with PyTest (including ML endpoint tests)
- Optional: background jobs (Celery) and Docker Compose

## Quick Start

### 1. Clone and setup
```bash
git clone https://github.com/BronkstoneBro/taskflow-fastapi
cd taskflow-fastapi
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the application
```bash
python main.py
```

After start:
- Swagger UI: `http://localhost:8000/docs`

### 3. Test the API
- Create a task:
  ```bash
  curl -X POST "http://localhost:8000/tasks" \
    -H "Content-Type: application/json" \
    -d '{"title": "Test task", "description": "Testing"}'
  ```
- Get all tasks:
  ```bash
  curl http://localhost:8000/tasks
  ```
- Update a task:
  ```bash
  curl -X PUT "http://localhost:8000/tasks/1" \
    -H "Content-Type: application/json" \
    -d '{"completed": true}'
  ```
- Delete a task:
  ```bash
  curl -X DELETE http://localhost:8000/tasks/1 -i
  ```

POST `/tasks` returns HTTP 201 and a `Location` header pointing to the created resource.

### 4. ML API Usage

Predict task priority using machine learning:

```bash
# Predict high priority task
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Fix critical security vulnerability"}'

# Expected response:
# {
#   "task_description": "Fix critical security vulnerability",
#   "predicted_priority": "high",
#   "confidence": {"high": 0.72, "low": 0.28}
# }
```

```bash
# Predict low priority task
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"task_description": "Update documentation"}'

# Expected response:
# {
#   "task_description": "Update documentation",
#   "predicted_priority": "low",
#   "confidence": {"high": 0.20, "low": 0.80}
# }
```

The ML model is trained on task descriptions and can classify tasks as either `high` or `low` priority with confidence scores.

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run only API tests
python -m pytest tests/test_api.py -v

# Run only ML tests
python -m pytest tests/test_ml_api.py -v
```

Tests include:
- `tests/test_api.py` - Full CRUD and validation tests
- `tests/test_ml_api.py` - ML endpoint prediction tests

## Project structure

```
src/
├── api/        # FastAPI app and routes
├── core/       # Pydantic models and in‑memory repository
└── tasks/      # (optional) Celery tasks and config
ml/
├── train_model.py    # ML model training script
└── predictor.py      # ML prediction logic
models/         # Trained ML models (*.pkl files)
docker/         # (optional) Docker & Compose
data/           # CSV files (training data + background job exports)
tests/          # Unit tests (API + ML endpoint tests)
main.py         # Entry point: imports app from src.api.main and runs Uvicorn
```

## Advanced Features

### Machine Learning Setup

The ML model needs to be trained before use:

```bash
# Train the model (creates models/priority_classifier.pkl)
python ml/train_model.py

# The model is automatically loaded when the API starts
python main.py
```

The model uses:
- **Algorithm**: Naive Bayes with TF-IDF vectorization
- **Training Data**: `data/tasks.csv` (task descriptions + priority labels)
- **Classes**: `high`, `low` priority
- **Features**: Text-based task descriptions

### Background Jobs (Celery)

Background endpoints are available only if Celery/Redis are installed and workers are running. The core API works without them.

### Local (no Docker)
Requires a running Redis (`REDIS_URL`, default `redis://localhost:6379/0`).

```bash
# run in separate processes
redis-server
celery -A src.tasks.celery_config worker --loglevel=info
python main.py

# trigger background job and check active tasks (if Celery enabled)
curl -X POST http://localhost:8000/api/fetch-users
curl http://localhost:8000/api/tasks/active
```

### Docker Compose

```bash
cd docker
docker-compose up --build
```

Services:
- API: `http://localhost:8000/docs`
- (optional) Flower: `http://localhost:5555`

CSV files are written to `data/`.

## Architecture notes
- The repository is injected via FastAPI dependencies (`Depends`) and overridden in tests with `app.dependency_overrides`.
- Data is kept in memory and resets on server restarts.
- Pydantic v2: you can optionally migrate deprecated bits (e.g., `Config` / `json_encoders`) to modern `ConfigDict` and field serializers. This is an optional improvement and not required for this project to work.