-- MVP search uses PostgreSQL full text search.
-- pgvector is intentionally deferred until the approved dataset is large enough.

CREATE TEXT SEARCH CONFIGURATION public.quant_prep_english (
  COPY = pg_catalog.english
);

COMMENT ON TEXT SEARCH CONFIGURATION public.quant_prep_english IS
  'MVP full text search configuration; pgvector intentionally deferred.';

