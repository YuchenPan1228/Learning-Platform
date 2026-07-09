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
pip install -e .
```

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check: `GET http://127.0.0.1:8000/health`
