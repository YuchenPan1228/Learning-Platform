# Quant Prep AI Roadmap

This roadmap must be approved before implementation begins.

The MVP is intentionally single-user, local-first, and free to run. Do not add new product features during Phases 0-2. Finish the MVP, use it personally, gather feedback, then iterate.

## Phase -1: Design and Architecture

Goal: make the major technical decisions before writing code.

### QP--001: Create Architecture Decision Records

Estimate: 2-4 hours

Tasks:

- Create ADR template.
- Record stack decisions: Next.js, FastAPI, PostgreSQL, Redis, local Ollama AI provider.
- Record delayed decisions: authentication, hosted deployment, paid crawlers, vector embeddings.

Depends on: none.

### QP--002: Draft Database ER Diagram

Estimate: 2-4 hours

Tasks:

- Model topics, concepts, concept edges, questions, tags, flashcards, attempts, resources, ingestion jobs, extracted objects, AI usage logs.
- Mark MVP tables vs later tables.
- Identify indexes and uniqueness constraints.

Depends on: `QP--001`.

### QP--003: Draft REST API / OpenAPI Specification

Estimate: 3-4 hours

Tasks:

- Define read APIs for topics, concepts, questions, flashcards, learning paths.
- Define practice attempt APIs.
- Define admin review APIs.
- Define AI explanation and generation APIs behind `AIProvider`.
- Keep auth out of the MVP API.

Depends on: `QP--002`.

### QP--004: Create Frontend Route Map

Estimate: 1-3 hours

Tasks:

- Define routes for dashboard, topics, concept pages, practice, mental math, flashcards, admin import, admin review.
- Mark MVP routes vs later routes.
- Define route-level data dependencies.

Depends on: `QP--003`.

### QP--005: Design Knowledge Graph

Estimate: 2-4 hours

Tasks:

- Define `Concept` and `ConceptEdge`.
- Support `requires`, `related_to`, and `used_in`.
- Define how graph neighbors appear on concept pages.
- Define how prerequisites inform tutoring and recommendations.

Depends on: `QP--002`.

### QP--006: Create Basic UI Wireframes

Estimate: 3-4 hours

Tasks:

- Dashboard wireframe.
- Topic library wireframe.
- Concept page wireframe.
- Practice page wireframe.
- Mental math wireframe.
- Admin review wireframe.

Depends on: `QP--004`.

## Phase 0: Project Foundation and Quality Gates

Goal: create the local development base and automated checks.

### QP-001: Initialize Repository Structure

Estimate: 1-2 hours

Tasks:

- Create `apps/web`, `apps/api`, `apps/worker`, `docs`, `infra`, and `scripts`.
- Add `.env.example`.
- Document local-only MVP assumptions.

Depends on: Phase -1 approval.

### QP-002: Add Local Docker Services

Estimate: 2-3 hours

Tasks:

- Add PostgreSQL.
- Add Redis.
- Enable PostgreSQL full text search.
- Do not add pgvector to the MVP path yet.

Depends on: `QP-001`.

### QP-003: Configure Backend App Shell

Estimate: 2-4 hours

Tasks:

- Add FastAPI app.
- Add health check.
- Add config loading.
- Add database connection.

Depends on: `QP-002`.

### QP-004: Configure Frontend App Shell

Estimate: 2-4 hours

Tasks:

- Add Next.js, TypeScript, Tailwind, and shadcn/ui.
- Add base app layout.
- Keep app single-user and unauthenticated.

Depends on: `QP-001`.

### QP-005: Add CI/CD Quality Gates

Estimate: 3-4 hours

Tasks:

- Add GitHub Actions.
- Add backend checks: `pytest`, `ruff`, `mypy`, coverage.
- Add frontend checks: `eslint`, `prettier`, type check.
- Require all checks to pass for every PR.

Depends on: `QP-003`, `QP-004`.

### QP-006: Add Backend Test Harness

Estimate: 2-4 hours

Tasks:

- Configure pytest.
- Add test database setup.
- Add coverage reporting.
- Add first health check test.

Depends on: `QP-003`, `QP-005`.

## Phase 1: Core Data Model

Goal: support the learning MVP without AI or automated ingestion.

### QP-007: Define MVP Database Models

Estimate: 3-4 hours

Tasks:

- Add Topic.
- Add Concept.
- Add ConceptEdge with `requires`, `related_to`, `used_in`.
- Add Question.
- Add Tag and QuestionTag.
- Add Flashcard.
- Add LearningPath and LearningPathStep.
- Add Attempt.
- Add UserTopicMastery placeholder, still single-user.

Depends on: `QP-006`.

### QP-008: Add Alembic Migrations

Estimate: 2-3 hours

Tasks:

- Create initial schema migration.
- Add key indexes for slugs, topic hierarchy, difficulty, tags, and full text search.

Depends on: `QP-007`.

### QP-009: Seed Topic Hierarchy and Knowledge Graph

Estimate: 2-4 hours

Tasks:

- Seed README topic hierarchy.
- Seed initial concepts.
- Seed prerequisite and related concept edges.

Depends on: `QP-008`.

### QP-010: Seed MVP Content

Estimate: 2-4 hours

Tasks:

- Seed 20 probability questions.
- Seed 20 mental math prompts.
- Seed 10 coding concept prompts.
- Seed 10 finance questions.
- Seed 5 market game placeholders.
- Keep all seed content hand-authored.

Depends on: `QP-009`.

### QP-011: Add Basic Read APIs

Estimate: 2-4 hours

Tasks:

- Topics API.
- Concepts API.
- Questions API.
- Flashcards API.
- Learning paths API.

Depends on: `QP-010`.

### QP-012: Add PostgreSQL Full Text Search

Estimate: 2-4 hours

Tasks:

- Add full text indexes for questions and concepts.
- Add search endpoint.
- Track search misses for later active learning.
- Do not use embeddings in MVP.

Depends on: `QP-011`.

### QP-013: Add Hash-Based Duplicate Detection

Estimate: 2-4 hours

Tasks:

- Normalize question text.
- Store normalized text hash.
- Detect exact and near-normalized duplicates.
- Leave vector similarity for a later phase.

Depends on: `QP-010`.

## Phase 2: Learning MVP

Goal: build a usable local learning product. No new features should be added during this phase.

### QP-014: Build Dashboard Page

Estimate: 2-4 hours

Tasks:

- Daily plan placeholder.
- Mastery cards.
- Weak prerequisite panel.
- Local single-user state.

Depends on: `QP-004`, `QP-011`.

### QP-015: Build Topic Library Page

Estimate: 2-4 hours

Tasks:

- Deep topic cards.
- Subtopic display.
- Search/filter by topic and concept.

Depends on: `QP-011`, `QP-012`.

### QP-016: Build Concept Page

Estimate: 3-4 hours

Tasks:

- Definition.
- Formula.
- Intuition.
- Mistakes.
- Interview tips.
- Related graph neighbors.

Depends on: `QP-011`.

### QP-017: Build Question Browser

Estimate: 3-4 hours

Tasks:

- Filter by topic, concept, difficulty, and tags.
- Show metadata and estimated time.

Depends on: `QP-011`, `QP-012`.

### QP-018: Build Practice Session Page

Estimate: 3-4 hours

Tasks:

- Question view.
- Answer input.
- Solution reveal.
- Metadata display.
- Deterministic self-check for supported questions.

Depends on: `QP-017`.

### QP-019: Build Mental Math Drill

Estimate: 2-4 hours

Tasks:

- Prompt queue.
- Deterministic answer checking.
- Category filter.
- No AI grading.

Depends on: `QP-010`.

### QP-020: Build Flashcard Review Page

Estimate: 2-4 hours

Tasks:

- Flip card.
- Mark again/good/easy.
- Store local review events.

Depends on: `QP-011`.

### QP-021: Record Attempts

Estimate: 2-4 hours

Tasks:

- Save answer.
- Save correctness where deterministic.
- Save time spent.
- Save question and topic IDs.

Depends on: `QP-018`.

## Phase 3A: AI Tutor and Generation

Goal: add AI only where deterministic code cannot solve the problem.

### QP-022: Add AIProvider Interface

Estimate: 2-4 hours

Tasks:

- Define provider interface.
- Add Ollama as default local provider.
- Add provider configuration.
- Leave OpenAI/Anthropic as later adapters.
- Route chat requests by task (`general`, `coding`, `reasoning`) with `OLLAMA_CHAT_MODEL` as the local fallback.
- Prefer JSON Schema structured outputs and schema validation; keep repair retries off by default.
- Split hint and explanation generation so each UI action only pays for what it needs.

Depends on: `QP-003`.

### QP-023: Track AI Usage

Estimate: 2-4 hours

Tasks:

- Record provider.
- Record model.
- Record tokens where available.
- Record latency.
- Record estimated cost.
- Record cache hit/miss.

Depends on: `QP-022`.

### QP-024: Add AI Result Cache

Estimate: 2-4 hours

Tasks:

- Cache explanations.
- Cache summaries.
- Cache generated questions.
- Cache by prompt hash, model, provider, and input object version.

Depends on: `QP-023`.

### QP-025: Add AI Explanation Endpoint

Estimate: 2-4 hours

Tasks:

- Question + user answer -> explanation.
- Include hints and common mistakes.
- Use cached result when available.

Depends on: `QP-024`, `QP-021`.

### QP-026: Add Similar Question Generation

Estimate: 3-4 hours

Tasks:

- Generate original variants.
- Store generated outputs as drafts.
- Preserve `generated_from`.
- Use background job where possible.

Depends on: `QP-024`, `QP-013`.

### QP-027: Wire AI Tutor Into Practice UI

Estimate: 2-4 hours

Tasks:

- Request hint.
- Request explanation.
- Request similar question.
- Show cache state only in developer/admin mode.

Depends on: `QP-025`, `QP-026`.

## Phase 3B: Mastery, Review, and Analytics

Goal: add adaptive learning without overusing AI.

### QP-028: Add Mastery Calculation

Estimate: 2-4 hours

Tasks:

- Compute topic and concept mastery from attempts.
- No AI required.

Depends on: `QP-021`.

### QP-029: Add Spaced Repetition Scheduling

Estimate: 2-4 hours

Tasks:

- Implement deterministic review scheduling.
- Update flashcard next review dates.

Depends on: `QP-020`, `QP-028`.

### QP-030: Add Study Planner

Estimate: 3-4 hours

Tasks:

- Use mastery, review due dates, and learning paths.
- Generate daily plan deterministically.
- Do not use AI for planning in MVP.

Depends on: `QP-028`, `QP-029`.

### QP-031: Add Learning Analytics Dashboard

Estimate: 3-4 hours

Tasks:

- Weak concepts.
- Attempt history.
- Review due count.
- Search misses.

Depends on: `QP-028`, `QP-030`.

## Phase 4: Admin Review and Manual Ingestion

Goal: add human-in-the-loop content review before automated collection. Manual import creates review-queue drafts as **questions** or **flashcards** only. **Existing concepts** are curated separately; manual import does not create new concepts or topics.

### Phase 4 design notes

**Draft targets:** User chooses whether an import becomes a question or flashcard. Publish converts approved drafts into `Question` or `Flashcard` records only.

**Topic assignment:**

| Phase | Topic assignment |
| --- | --- |
| Phase 4 (now) | User picks topic and optional subtopic at import and can change them in review |
| Phase 5 | AI pre-fills `topic_slug` / `subtopic_slug` from source content; user confirms in review |
| Later | Optional auto-suggest with override |

**AI processing:**

- Phase 4: import URL/PDF metadata or pasted text; user writes or edits draft content in review before publish.
- Phase 5 (`QP-042`, `QP-043`): local page/PDF extraction and structured AI extraction into the same review queue.
- Do not build a second AI extraction path in Phase 4; it would duplicate Phase 5 work.

**Concept curation:** Editing **existing** seeded concepts (definition, formula, intuition, tips, etc.) is tracked in `QP-038` and is separate from the import → review → publish loop for questions and flashcards.

### QP-032: Add Ingestion Data Models

Estimate: 3-4 hours

Tasks:

- Add TopicJob.
- Add Resource.
- Add ExtractedObject.
- Add LearningSignal.
- Add job execution logs.
- Add AI usage relation where relevant.

Depends on: `QP-007`, `QP-023`.

### QP-033: Add Job Observability

Estimate: 2-4 hours

Tasks:

- Log start time.
- Log finish time.
- Log runtime.
- Log failure reason.
- Log source URL.
- Log model used.
- Log token usage.
- Log estimated cost.

Depends on: `QP-032`.

### QP-034: Build Admin Import Form

Estimate: 2-4 hours

Tasks:

- Add manual URL import.
- Add manual note import.
- Add pasted question import.
- Add local PDF metadata import.
- Require user-selected topic, optional subtopic, and draft type (question or flashcard).
- Keep crawling and PDF parsing deferred to Phase 5.

Depends on: `QP-032`.

### QP-035: Build Review Queue API

Estimate: 2-4 hours

Tasks:

- List drafts.
- Approve draft.
- Edit draft.
- Reject draft.
- Preserve provenance.

Depends on: `QP-032`.

### QP-036: Build Admin Review UI

Estimate: 3-4 hours

Tasks:

- Show source, extracted text, and provenance metadata.
- Show license status and quality score.
- Edit draft content (question or flashcard fields, topic, subtopic).
- Approve, reject, and publish approved drafts.
- Show formulas and candidate questions when present in payload (for future AI extraction).

Depends on: `QP-035`.

### QP-037: Publish Approved Drafts

Estimate: 4-6 hours

Tasks:

- Create a linked ExtractedObject draft when a Resource is imported; return `extracted_object_id` from import APIs.
- Restrict manual import draft types to question and flashcard.
- Validate `topic_slug` and optional `subtopic_slug` against the topic hierarchy.
- Map pasted note, URL, PDF, and question imports into question or flashcard payload shapes.
- Add draft/approved/rejected queue tabs in the review UI.
- Edit draft payload, object type, topic, and quality score before approval.
- Convert approved ExtractedObject into Question or Flashcard.
- Publish approved drafts from the review UI; surface publish duplicate errors (409).
- Do not create new Concept or Topic records from manual import.
- Reuse hash-based duplicate detection.
- Keep generated variants traceable.
- Link import success UI to the review queue.

Depends on: `QP-034`, `QP-035`, `QP-036`, `QP-013`.

### QP-038: Add Admin Concept Editor

Estimate: 3-4 hours

Tasks:

- List existing concepts by topic.
- Edit definition, formula, intuition, worked example, common mistakes, and interview tips.
- Preserve slug and graph edges unless explicitly changed.
- Keep concept creation out of manual import; new concepts remain a separate curation workflow.

Depends on: `QP-011`, `QP-016`.

## Phase 5: Knowledge Ingestion Pipeline

Goal: topic-driven automated drafting into the same review queue as Phase 4, still reviewed by a human. Avoid paid crawler services. AI proposes question/flashcard drafts and topic suggestions; the user confirms before publish.

### QP-039: Implement Topic Job Lifecycle

Estimate: 2-4 hours

Tasks:

- Queued.
- Collecting.
- Extracting.
- Reviewing.
- Completed.
- Failed.

Depends on: `QP-032`, `QP-033`, `QP-037`.

### QP-040: Add Source Policy Checker

Estimate: 2-3 hours

Tasks:

- Allowlist support.
- Robots status.
- License status.
- Attribution requirement.

Depends on: `QP-039`.

### QP-041: Add Source Quality Scoring

Estimate: 3-4 hours

Tasks:

- Domain reputation.
- Content length.
- Formula density.
- Code examples.
- Educational structure.
- Human review rating.

Depends on: `QP-040`.

### QP-042: Add Local Page Extraction

Estimate: 3-4 hours

Tasks:

- Use requests.
- Use BeautifulSoup.
- Use Trafilatura.
- Use Playwright only when needed.
- Use PyMuPDF for PDFs.
- Do not use Firecrawl in MVP.

Depends on: `QP-040`.

### QP-043: Add Structured AI Extraction

Estimate: 3-4 hours

Tasks:

- Extract candidate questions and flashcards from page or PDF text.
- Extract summaries and source metadata for review.
- Suggest `topic_slug` and optional `subtopic_slug`; user confirms in review.
- Use Ollama via `AIProvider`.
- Defer automatic concept, formula, and example creation until `QP-038` concept editor and graph curation workflow exist.

Depends on: `QP-024`, `QP-042`.

### QP-044: Store Extracted Typed Objects

Estimate: 2-4 hours

Tasks:

- Save payload JSON.
- Save confidence score.
- Save extraction method.
- Save model version.
- Save provenance.

Depends on: `QP-043`.

### QP-045: Add Normalized Text Deduplication for Extracted Objects

Estimate: 2-4 hours

Tasks:

- Normalize extracted question text.
- Compare hashes.
- Compare normalized strings.
- Suggest canonical object.
- Do not use embeddings yet.

Depends on: `QP-044`, `QP-013`.

### QP-046: Surface Dedupe and Quality in Review UI

Estimate: 2-3 hours

Tasks:

- Show duplicate matches.
- Show source quality score.
- Show policy status.
- Show provenance.

Depends on: `QP-036`, `QP-037`, `QP-045`.

## Phase 6: Embeddings and Semantic Search

Goal: add vector search only after there is enough content to justify it.

### QP-047: Evaluate Dataset Size and Embedding Need

Estimate: 1-2 hours

Tasks:

- Count approved questions, concepts, flashcards.
- Identify search quality gaps.
- Decide whether embeddings are worth adding.

Depends on: `QP-046`.

### QP-048: Add Local Embedding Provider

Estimate: 2-4 hours

Tasks:

- Use local embedding model such as `nomic-embed-text` or `bge-small-en-v1.5`.
- Keep provider swappable.
- Track embedding runtime and cost as zero/local.
- Wire the reserved `AITask.EMBEDDING` / `OLLAMA_EMBEDDING_MODEL` config into the embedding provider.

Depends on: `QP-047`.

### QP-049: Add pgvector

Estimate: 2-4 hours

Tasks:

- Enable pgvector.
- Add vector columns.
- Add vector indexes.

Depends on: `QP-048`.

### QP-050: Add Semantic Duplicate Clustering

Estimate: 3-4 hours

Tasks:

- Cluster near-duplicate questions.
- Suggest canonical record.
- Store similarity scores.

Depends on: `QP-049`.

### QP-051: Add Hybrid Search

Estimate: 3-4 hours

Tasks:

- Combine full text and vector search.
- Rank by quality score and relevance.
- Keep full text search available as fallback.

Depends on: `QP-050`.

## Phase 7: Active Learning

Goal: make the system improve from user behavior.

### QP-052: Track Search Misses

Estimate: 2-3 hours

Tasks:

- Record empty and low-quality search results.
- Store LearningSignal.

Depends on: `QP-012`, `QP-032`.

### QP-053: Add Confusing Question Flag

Estimate: 1-3 hours

Tasks:

- User can flag confusing question.
- Create LearningSignal.

Depends on: `QP-018`, `QP-032`.

### QP-054: Promote and Demote Content Quality

Estimate: 3-4 hours

Tasks:

- Use completion rate.
- Use retry rate.
- Use flag count.
- Update quality signals.

Depends on: `QP-021`, `QP-053`.

### QP-055: Suggest Topic Jobs from Learning Signals

Estimate: 3-4 hours

Tasks:

- Search misses suggest topic jobs.
- Weak concepts suggest content generation.
- Frequent confusion suggests review queue items.

Depends on: `QP-052`, `QP-054`, `QP-039`.

## Phase 8: Interactive Market Games

Goal: add differentiating quant interview practice after the MVP is stable.

### QP-056: Add Market Game Data Model

Estimate: 2-4 hours

Tasks:

- Game type.
- Parameters.
- Scoring.
- Attempts.

Depends on: `QP-007`.

### QP-057: Implement Monty Hall Game

Estimate: 2-4 hours

Tasks:

- Interactive deterministic game.
- Explanation.
- Attempt tracking.

Depends on: `QP-056`.

### QP-058: Implement Guess 2/3 Average Game

Estimate: 3-4 hours

Tasks:

- Single-player simulation.
- AI or fixed-strategy population.
- Score and explanation.

Depends on: `QP-056`.

### QP-059: Implement Basic Market Making Spread Game

Estimate: 3-4 hours

Tasks:

- Bid/ask choices.
- Simple inventory state.
- Deterministic scoring.

Depends on: `QP-056`.

## Phase 9: Authentication and Deployment

Goal: move beyond local single-user mode only after the core product works.

### QP-060: Choose Auth Provider

Estimate: 1-2 hours

Tasks:

- Compare Auth.js and Clerk.
- Decide local/dev behavior.
- Decide account model.

Depends on: MVP feedback.

### QP-061: Add Authentication

Estimate: 3-4 hours

Tasks:

- Add chosen provider.
- Add protected routes.
- Migrate single-user assumptions.

Depends on: `QP-060`.

### QP-062: Add Hosted Deployment

Estimate: 3-4 hours

Tasks:

- Pick hosting target.
- Add production env config.
- Add deployment pipeline.

Depends on: `QP-061`.

## Final Review

### QP-999: Architecture Review

Estimate: 4+ hours

Tasks:

- Remove duplicate abstractions.
- Improve folder structure.
- Improve naming consistency.
- Optimize database indexes.
- Improve API consistency.
- Remove dead code.
- Run security review.
- Run performance review.
- Run test coverage review.
- Produce technical debt report.

Depends on: completion of major milestone selected for release.

