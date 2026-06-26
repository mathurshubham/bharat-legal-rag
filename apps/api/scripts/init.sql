CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_search;

CREATE TABLE IF NOT EXISTS chunks (
    id          BIGSERIAL PRIMARY KEY,
    demo_id     TEXT        NOT NULL,
    doc_id      TEXT        NOT NULL,
    doc_title   TEXT        NOT NULL,
    section_ref TEXT        NOT NULL,
    chunk_index INT         NOT NULL,
    content     TEXT        NOT NULL,
    tokens      INT         NOT NULL DEFAULT 0,
    visibility  TEXT        NOT NULL DEFAULT 'public',  -- public | internal | confidential
    embedding   vector(1024),
    metadata    JSONB       NOT NULL DEFAULT '{}',
    embed_model TEXT,
    embed_manifest JSONB
);

CREATE INDEX IF NOT EXISTS chunks_hnsw ON chunks
    USING hnsw (embedding vector_cosine_ops);

-- demo_id + visibility included in BM25 index so retrieval predicate fuses into the index walk
-- (applied as heap_filter during the walk — single-step, no post-scan)
CREATE INDEX IF NOT EXISTS chunks_bm25 ON chunks
    USING bm25 (id, content, doc_title, section_ref, demo_id, visibility)
    WITH (key_field='id');

CREATE INDEX IF NOT EXISTS chunks_demo_doc ON chunks (demo_id, doc_id);
CREATE INDEX IF NOT EXISTS chunks_demo_section ON chunks (demo_id, doc_id, section_ref);
CREATE INDEX IF NOT EXISTS chunks_demo_visibility ON chunks (demo_id, visibility);
