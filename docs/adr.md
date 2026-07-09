# Architecture Decision Records

This file records current pre-implementation decisions. Each decision can later be split into one ADR file if the project grows.

## ADR-001: Build a Single-User Local MVP

Status: Accepted

Decision:

- The MVP will run locally.
- The MVP will not include authentication.
- The MVP will assume one user.

Rationale:

- Faster iteration.
- No auth complexity before product fit.
- Lower deployment and data privacy overhead.

Consequences:

- User-specific tables may use a local default user or nullable user fields initially.
- Authentication will require a later migration.

## ADR-002: Delay Authentication

Status: Accepted

Decision:

- Do not implement Auth.js, Clerk, or custom auth during Phases 0-2.
- Revisit authentication after MVP feedback.

Rationale:

- Auth does not prove the core learning loop.
- Local single-user progress is enough for early usage.

## ADR-003: Use Ollama as the Default AI Provider

Status: Accepted

Decision:

- Use Ollama by default for local AI.
- Keep model access behind `AIProvider`.
- Add OpenAI/Anthropic only as later adapters.

Rationale:

- Local development should be free.
- Provider abstraction avoids lock-in.

## ADR-004: Split AI Into 3A and 3B

Status: Accepted

Decision:

- Phase 3A: AI explanations, hints, similar question generation.
- Phase 3B: mastery calculation, spaced repetition, study planner, learning analytics.

Rationale:

- AI tutoring and deterministic learning analytics have different risks.
- Mastery and scheduling should not depend on LLMs.

## ADR-005: Delay Embeddings

Status: Accepted

Decision:

- Do not implement embeddings in the MVP.
- Start with PostgreSQL Full Text Search.
- Use hash-based and normalized text duplicate detection.
- Add local embeddings and pgvector only after content volume justifies them.

Rationale:

- Embeddings add complexity before there is enough data.
- Full text search is simpler and sufficient for the first dataset.

## ADR-006: Add CI/CD in Phase 0

Status: Accepted

Decision:

- Add GitHub Actions early.
- Include pytest, ruff, mypy, eslint, prettier, and coverage checks.

Rationale:

- The project has multiple moving parts.
- Automated checks prevent drift as the app grows.

## ADR-007: Add Observability for Jobs and AI Usage

Status: Accepted

Decision:

- Every ingestion/background job logs timing, status, failure reason, source URL, model, token usage, and estimated cost where applicable.
- Every AI request records provider, model, tokens, latency, estimated cost, and cache status.

Rationale:

- Ingestion and AI systems are difficult to debug without traces.
- Cost and latency should be visible from the beginning.

## ADR-008: Keep the Knowledge Graph First-Class

Status: Accepted

Decision:

- Add `Concept` and `ConceptEdge` to the core data model.
- Support `requires`, `related_to`, and `used_in`.

Rationale:

- The graph powers prerequisites, tutoring context, review planning, and concept pages.

## ADR-009: Use Local Ingestion Tools for the MVP

Status: Accepted

Decision:

- Start with requests, BeautifulSoup, Trafilatura, Playwright only when needed, and PyMuPDF.
- Do not use Firecrawl or paid crawler services in the MVP.

Rationale:

- Local development should remain free.
- Paid services can be evaluated after the pipeline proves useful.

## ADR-010: Freeze MVP Scope Through Phase 2

Status: Accepted

Decision:

- Do not add features during Phases 0-2 beyond the approved MVP.

Rationale:

- The fastest path to a useful product is finishing the core learning loop before expanding.

