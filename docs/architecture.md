# Quant Prep AI Architecture

This document captures the pre-implementation architecture direction. It should be reviewed with `docs/product-roadmap.md` before Phase 0 begins.

## Core Principles

- Build a single-user local MVP first.
- Do not implement authentication in the MVP.
- Keep local development completely free.
- Use deterministic code before AI.
- Use AI only for tasks that require language understanding or generation.
- Cache every AI-generated result.
- Prefer offline/background AI jobs over request-time generation.
- Avoid paid crawler services in the MVP.
- Delay embeddings until the dataset is large enough to need semantic search.
- Keep all AI providers behind an interface.
- Treat ingestion as a Knowledge Ingestion Pipeline, not a scraper.

## Initial Architecture

```mermaid
flowchart TD
    Web["Next.js Web App"]
    API["FastAPI API"]
    Worker["Background Worker"]
    DB["PostgreSQL"]
    Redis["Redis Queue/Cache"]
    Ollama["Ollama Local Models"]
    Ingestion["Knowledge Ingestion Pipeline"]

    Web --> API
    API --> DB
    API --> Redis
    Worker --> Redis
    Worker --> DB
    API --> Ollama
    Worker --> Ollama
    Worker --> Ingestion
    Ingestion --> DB
```

## Local-First MVP

The MVP should run locally without paid services.

Required local services:

- Next.js frontend
- FastAPI backend
- Background worker
- PostgreSQL
- Redis
- Ollama

Not included in MVP:

- Authentication
- Hosted deployment
- Paid crawler services
- Paid AI APIs
- Vector embeddings
- pgvector
- Multiplayer or collaborative features

## AI Provider Design

All model calls must go through an `AIProvider` abstraction.

Default provider:

- Ollama

Likely local models:

- Qwen
- Gemma
- Llama
- Mistral

Possible later providers:

- OpenAI
- Anthropic
- Google

Every AI request must record:

- Provider
- Model
- Input tokens, when available
- Output tokens, when available
- Latency
- Estimated cost
- Cache hit or miss
- Prompt hash
- Input object version
- Created timestamp

Use AI for:

- Explanations
- Hints
- Summarization
- Concept extraction
- Question generation
- Classification

Do not use AI for:

- Deterministic math grading
- Flashcard scheduling
- Progress tracking
- Filtering
- Search
- Hash-based duplicate detection

## AI Caching

Every AI-generated result should be cached by:

- Provider
- Model
- Prompt template version
- Input hash
- Relevant object version

Cached objects:

- Explanations
- Hints
- Summaries
- Generated question variants
- Structured extraction outputs
- Classification outputs

The UI should not regenerate AI output unless explicitly requested.

## Search and Deduplication Strategy

MVP search:

- PostgreSQL Full Text Search
- Filters by topic, concept, difficulty, tags, and metadata

MVP deduplication:

- Raw text hash
- Normalized text hash
- Normalized string comparison

Later search:

- Local embeddings
- pgvector
- Hybrid full text + vector ranking

Later deduplication:

- Embedding similarity
- Duplicate clusters
- Canonical record suggestions

## Knowledge Graph

The knowledge graph is a first-class learning primitive.

Core models:

- `Concept`
- `ConceptEdge`

Supported relationship types:

- `requires`
- `related_to`
- `used_in`

Primary uses:

- Concept page related links
- Prerequisite warnings
- Study path sequencing
- AI tutor context
- Weakness diagnosis
- Ingestion classification

Example:

```text
Conditional Probability --requires--> Counting
Bayes --requires--> Conditional Probability
Bayes --related_to--> Base Rates
Bayes --used_in--> Medical Testing Problems
```

## Knowledge Ingestion Pipeline

The pipeline is topic-driven.

Example input:

```text
Topic job: Conditional Probability
```

Pipeline stages:

1. Create topic job.
2. Collect candidate sources.
3. Check source policy.
4. Score source quality.
5. Extract content locally.
6. Use AI for structured extraction only when needed.
7. Store extracted typed objects.
8. Detect duplicates with normalized text.
9. Send drafts to human review.
10. Publish approved knowledge objects.

MVP crawler tools:

- requests
- BeautifulSoup
- Trafilatura
- Playwright only when needed
- PyMuPDF for PDFs

Do not use Firecrawl in the MVP.

## Ingestion Observability

Every ingestion and background job must log:

- Job ID
- Stage
- Start time
- Finish time
- Runtime
- Status
- Failure reason
- Source URL, when applicable
- Model used, when applicable
- Token usage, when applicable
- Estimated cost, when applicable

This applies to:

- Topic jobs
- Source collection
- Source scoring
- Page extraction
- PDF extraction
- Structured AI extraction
- AI generation
- Draft publishing

## Data Model Areas

Learning core:

- Topic
- Concept
- ConceptEdge
- Question
- Tag
- QuestionTag
- Flashcard
- LearningPath
- LearningPathStep
- Attempt
- UserTopicMastery

Ingestion:

- TopicJob
- Resource
- ExtractedObject
- JobExecutionLog
- LearningSignal

AI:

- AIUsageLog
- AICacheEntry

Later vector search:

- Embedding provider metadata
- Vector columns
- DuplicateCluster

## API Areas

MVP APIs:

- Topics
- Concepts
- Questions
- Flashcards
- Learning paths
- Search
- Attempts

Phase 3A APIs:

- AI explanations
- AI hints
- Similar question generation

Phase 3B APIs:

- Mastery
- Spaced repetition
- Study planner
- Learning analytics

Phase 4-5 APIs:

- Admin import
- Review queue
- Topic jobs
- Ingestion job status

No authentication should be added until a later milestone.

## Frontend Routes

MVP routes:

- `/`
- `/topics`
- `/topics/[slug]`
- `/concepts/[slug]`
- `/practice`
- `/mental-math`
- `/flashcards`
- `/admin/import`
- `/admin/review`

Later routes:

- `/analytics`
- `/market-games`
- `/admin/ingestion/jobs`
- `/settings`
- `/login`

## CI/CD Requirements

Phase 0 must include automated checks.

Backend:

- pytest
- ruff
- mypy
- coverage

Frontend:

- eslint
- prettier
- TypeScript type checking

Every PR should pass all checks before merging.

## Deferred Decisions

Authentication:

- Deferred until after local MVP feedback.
- Candidates: Auth.js or Clerk.

Deployment:

- Deferred until after MVP.

Paid AI providers:

- Deferred.
- Add through `AIProvider` adapters only.

Paid crawler services:

- Deferred.
- Evaluate only after local tooling proves insufficient.

Embeddings:

- Deferred until approved dataset size and search quality justify them.

