# Quant Prep API

FastAPI backend shell for the local MVP.

## Setup

From the repository root:

```bash
cp .env.example .env
./scripts/start-services.sh
```

Create a virtual environment and install dependencies:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Test

Requires PostgreSQL. From the repository root:

```bash
./scripts/start-services.sh
```

If your Docker volume was created before the test database was added:

```bash
docker compose exec postgres psql -U quant_prep -d quant_prep -c "CREATE DATABASE quant_prep_test;"
```

Run tests:

```bash
cd apps/api
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

Integration tests use `TEST_DATABASE_URL` and skip automatically when PostgreSQL is unavailable.

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check: `GET http://127.0.0.1:8000/health`
