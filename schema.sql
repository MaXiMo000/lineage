-- Phase 1 schema. Loaded automatically by docker compose on first start.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE traces (
  id          text PRIMARY KEY,                  -- short slug used in the share URL
  input_text  text,
  input_image text,                              -- object-store key, if the input was a screenshot
  status      text NOT NULL DEFAULT 'queued',    -- queued | running | done | failed
  sources     text[] NOT NULL DEFAULT '{}',      -- which sources were searched (shown to users as coverage)
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE candidates (
  id          bigserial PRIMARY KEY,
  trace_id    text NOT NULL REFERENCES traces(id) ON DELETE CASCADE,
  url         text NOT NULL,
  source      text NOT NULL,                     -- serpapi | chronam | gdelt | bluesky | reddit | tineye | ...
  snippet     text NOT NULL,                     -- store snippets, never full pages (copyright + cost)
  date        timestamptz,
  date_kind   text,                              -- platform | archive | metadata | search
  parent_id   bigint REFERENCES candidates(id),
  similarity  real,
  changes     jsonb NOT NULL DEFAULT '[]',       -- word diff vs parent
  labels      text[] NOT NULL DEFAULT '{}',      -- attribution_swap | number_change | entity_swap | ...
  pdq         bit(256),                          -- image hash when the candidate is an image
  embedding   vector(384),                       -- all-MiniLM-L6-v2 sized; change if you switch models
  UNIQUE (trace_id, url)
);
CREATE INDEX ON candidates (trace_id, date);

-- Cache every external lookup: archives and search APIs are slow, rate-limited, and paid.
CREATE TABLE http_cache (
  key        text PRIMARY KEY,                   -- source + normalized request
  body       jsonb NOT NULL,
  fetched_at timestamptz NOT NULL DEFAULT now()
);
