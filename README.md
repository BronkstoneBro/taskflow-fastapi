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

### 3. Test the API (via Swagger)
Use Swagger UI at `http://localhost:8000/docs`:

- Open `/tasks` → POST and click “Try it out”.
  - Example body: `{ "title": "Test task", "description": "Testing" }`
  - Execute; you should get HTTP 201 and the response will include a `Location` header pointing to the created resource.
- Open `/tasks` → GET to fetch all tasks.
- Open `/tasks/{task_id}` → PUT to update a task.
  - Example body: `{ "completed": true }`
- Open `/tasks/{task_id}` → DELETE to remove a task.

### 4. ML API Usage

**Interactive Documentation**: Open http://localhost:8000/docs and find the `/predict` endpoint

**Try it out with these examples:**

**High priority tasks:**
```json
{"task_description": "Fix critical security vulnerability"}
{"task_description": "Implement new API endpoint"}
{"task_description": "Optimize database performance"}
```

**Low priority tasks:**
```json
{"task_description": "Update documentation"}
{"task_description": "Clean up code comments"}
{"task_description": "Refactor variable names"}
```

**Response format:**
```json
{
  "task_description": "your input text",
  "predicted_priority": "high" | "low",
  "confidence": {
    "high": 0.72,
    "low": 0.28
  }
}
```

The ML model uses Naive Bayes with TF-IDF to classify task descriptions into `high` or `low` priority with confidence scores.

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