# Local MVP Assumptions

These assumptions apply through Phases 0-2 unless the roadmap is explicitly revised.

- The MVP is single-user.
- The MVP runs in local development only.
- Authentication is not implemented.
- Hosted deployment is not required.
- Local development should be free to run.
- Ollama is the default AI provider behind the `AIProvider` interface.
- Chat workloads are routed by task (`general` / `coding` / `reasoning`), with small local model defaults and larger production targets documented in architecture/ADR-011.
- Structured AI responses use JSON Schema + validation; repair retries stay off by default.
- PostgreSQL Full Text Search is used before embeddings.
- Hash-based and normalized-text duplicate detection are used before vector similarity.
- Paid crawler services are not used in the MVP.
- Features outside the approved MVP scope should wait until after Phases 0-2.

