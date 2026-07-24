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

## Migrations

Apply the latest schema:

```bash
cd apps/api
source .venv/bin/activate
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

## Seed knowledge graph

Load the README topic hierarchy, initial concepts, and concept edges:

```bash
cd apps/api
source .venv/bin/activate
alembic upgrade head
python -m app.seeds
```

The seed is idempotent and safe to rerun locally.

## Seed MVP content

Requires the knowledge graph seed first:

```bash
cd apps/api
source .venv/bin/activate
python -m app.seeds
python -m app.seeds.mvp_content
```

This loads 85 hand-authored questions: 20 probability, 20 mathematics, 20 mental math, 10 coding, 10 finance, and 5 market game placeholders, plus flashcards.

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check: `GET http://127.0.0.1:8000/health`

## Read APIs

Read-only endpoints for the MVP content model (no auth per ADR-001):

- `GET /topics` — root topics with nested subtopics
- `GET /topics/{slug}` — topic detail
- `GET /concepts` — list concepts (`topic_slug` filter optional)
- `GET /concepts/{slug}` — concept detail with graph neighbors
- `GET /questions` — paginated approved questions (`items`, `total`, `limit`, `offset`; filters: `topic_slug`, `subtopic_slug`, `difficulty`, …)
- `GET /questions/{question_id}` — question detail including solution fields
- `GET /flashcards` — paginated flashcards (`items`, `total`, `limit`, `offset`; `topic_slug`, `due_only`)
- `GET /flashcards/{flashcard_id}` — flashcard detail
- `GET /admin/flashcards` — list/edit/delete published flashcards

## Search

Full-text search uses the existing PostgreSQL GIN indexes (`quant_prep_english`) on questions and concepts. No embeddings (ADR-005).

- `GET /search?q=&types=&topic_slug=&difficulty=&limit=` — search questions and concepts
- Empty result sets are recorded as `search_miss` learning signals for later active learning

## Duplicate detection

Hash-based duplicate detection for questions (no embeddings per ADR-005):

- `GET /questions/{question_id}/duplicates` — exact raw, exact normalized, and near-normalized matches
- Question rows store `raw_text_hash`, `normalized_text_hash`, and `normalized_text` for ingestion and review flows
