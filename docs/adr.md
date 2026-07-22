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

## ADR-011: Route AI Workloads Across Specialized Models

Status: Accepted

Decision:

- Keep Ollama as the default local AI provider behind `AIProvider`.
- Route chat workloads by `AITask`: `general`, `coding`, `reasoning` (plus `embedding` later).
- Document production targets as Qwen3 32B (general), Qwen2.5-Coder 32B (coding), DeepSeek-R1 (reasoning), and `nomic-embed-text` (embeddings).
- Keep local defaults small via `OLLAMA_CHAT_MODEL`, with optional `OLLAMA_MODEL_*` overrides.
- Prefer JSON Schema structured outputs and Pydantic validation; keep repair retries off by default for latency.
- Warm the default chat model on API startup; stream responses and parallel multi-artifact generation in a later pass.

Rationale:

- One small model is enough to unlock the tutoring loop on a laptop.
- Specialized models improve coding and hard quant reasoning when hardware allows.
- Schema-constrained generation is more reliable than free-form “return JSON” prompts.

Consequences:

- Services must resolve models through task routing and cache by the resolved model name.
- Embedding calls remain deferred until QP-048; config/routing placeholders are reserved now.

## ADR-012: Manual Ingestion Publishes Questions and Flashcards Only

Status: Accepted

Decision:

- Phase 4 manual import creates review-queue drafts as questions or flashcards only.
- Publish converts approved drafts into `Question` or `Flashcard` records.
- Manual import does not create new `Concept` or `Topic` records.
- Editing **existing** seeded concepts is a separate admin workflow (`QP-038`), not part of import → review → publish.

Rationale:

- Questions and flashcards are the highest-value incremental content for interview prep.
- Concept and topic graph curation needs a dedicated editor and should not be coupled to URL/PDF ingestion.
- Keeps the human review loop narrow and testable before Phase 5 automation.

Consequences:

- `admin_publish` manual path supports question and flashcard only.
- Concept/formula/example extraction from automated ingestion stays deferred until `QP-038` exists.

## ADR-013: User-Chosen Topic at Import; AI Suggests in Phase 5

Status: Accepted

Decision:

- Phase 4: user selects topic and optional subtopic at import and may change them while editing a draft in review.
- Phase 5 (`QP-043`): AI may pre-fill `topic_slug` / `subtopic_slug` from source content; user confirms in review before approve/publish.
- Later: optional auto-suggest with override is allowed, but human confirmation remains required before publish.

Rationale:

- Topic placement errors are costly and hard to undo at scale.
- A single-user MVP should prefer explicit control until extraction quality is proven.
- AI suggestions fit naturally after structured extraction exists in Phase 5.

Consequences:

- Import APIs require validated `topic_slug`.
- Review UI must expose topic/subtopic editing on drafts.
- Phase 5 extractors should write suggested topics into `payload_json`, not publish directly.

## ADR-014: Defer URL/PDF AI Extraction to Phase 5

Status: Accepted

Decision:

- Phase 4 imports URL bookmarks and uploaded PDF files, then the user writes or edits draft content in review.
- Phase 4 stores uploaded PDFs on local disk under `UPLOAD_DIR` and links them from `Resource.url`; it does not parse PDF text yet.
- Phase 5 (`QP-042`, `QP-043`) adds local page/PDF text extraction and AI structured parsing into the same review queue.
- Phase 5 AI extraction must support: long webpage text → formatted Q&A drafts; uploaded PDF text → formatted Q&A drafts; pasted freeform notes → formatted Q&A / flashcard drafts.
- Do not build a parallel AI extraction path in Phase 4.

Rationale:

- Phase 5 already owns crawling, extraction tooling, and job lifecycle.
- Duplicating AI extraction in Phase 4 would fork provenance, observability, and review UX.
- Uploading the PDF now still lets reviewers keep the source next to the draft before extraction exists.

Consequences:

- Phase 4 URL imports create skeleton question or flashcard drafts with placeholders where needed.
- Phase 4 PDF imports require a file upload and create skeleton drafts linked to the stored file.
- Phase 5 must implement AI parsing that converts long source text into title/body/answer-style question drafts (and flashcards), not just raw text storage.
- Review UI is shared between manual and automated drafts through Phase 5 and beyond.

