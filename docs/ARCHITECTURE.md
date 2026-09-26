# lineage: architecture

## System

```
            ┌──────── web (Vite + TS, custom SVG graph) ────────────┐
            │  paste claim / upload screenshot → live tree via SSE  │
            └───────────────┬───────────────────────▲───────────────┘
                            │ POST /api/traces      │ GET /api/traces/{id}/events (SSE)
                    ┌───────▼───────────────────────┴───────┐
                    │ FastAPI (lineage.api)                 │
                    └───────┬───────────────────────▲───────┘
                     enqueue│                       │read
                    ┌───────▼───────┐        ┌──────┴───────────────┐
                    │ Redis + RQ    │        │ Postgres + pgvector  │
                    └───────┬───────┘        │ traces, candidates,  │
                            │                │ http_cache           │
                    ┌───────▼────────────────┴──────────────────────┐
                    │ worker: trace pipeline                        │
                    │ extract → queries → sources → date → filter   │
                    │ → build_tree → labels → persist → publish SSE │
                    └───────┬───────────────────────────────────────┘
                            │ (every call via http_cache)
      SerpAPI · Chronicling America · Google Books · IA · Wayback CDX · Fact Check API
      Bluesky · Reddit · GDELT · TinEye/Lens · Claude API
```

Why these choices:
- **Postgres for everything** (rows, vectors, and cache). One thing to back up. Add a dedicated vector DB only if pgvector gets slow.
- **RQ, not Celery.** Jobs are just "run a trace". RQ is ~0 config.
- **SSE, not WebSockets.** Data only flows one way, and SSE works through every proxy.
- **Snippets only.** This avoids copyright exposure and keeps the DB small.

## Trace pipeline (worker)

```python
def run_trace(trace_id):
    claim = extract(trace)                     # text as-is; screenshot → vision OCR → {text, handle, post_id, displayed_date}
    queries = generate_queries(claim.text)     # LLM, 10–20 strings, validated
    cands = []
    for src in SOURCES:                        # sequential, per-source budget + timeout
        for q in queries:
            cands += src.search(q, before=None)
        publish(trace_id, "source_done", src.name)
    cands = dedupe_by_url(cands)
    cands = [c for c in cands if relevant(claim.text, c.snippet)]
    for c in cands:
        c.date, c.date_kind = date_candidate(c) # best_date over platform/archive/metadata/search evidence
    tree = build_tree(cands)                   # lineage.tree
    label_edges(tree)                          # LLM, fixed enum
    persist(tree); publish(trace_id, "done")
```

## Algorithms

### Text fingerprinting (`lineage/fingerprint.py`)
- `normalize`: NFKC → lowercase → strip quotes/apostrophes → punctuation to spaces → collapse whitespace.
- `shingles(k=2)`: word bigrams. **k=2 on purpose**: viral quotes are 6–25 words, and with k=3 a single swapped
  word in a short quote wipes out every shared shingle (see `test_short_quote_attribution_swap_still_links`).
- `similarity`: exact Jaccard. Past ~2k candidates, move to **MinHash (128 perms) + LSH** (`datasketch`), with
  the same threshold semantics.
- Paraphrases that share no bigrams ("Einstein said insanity is…" vs "Insanity: doing the same…") need
  **embeddings**: `all-MiniLM-L6-v2` (384-d, matches `schema.sql`). Use `max(jaccard, cosine_rescaled)` for relevance.

### Image fingerprinting (Phase 3)
- **PDQ** (Meta, 256-bit): robust to re-encoding, resizing, and light edits. Match = Hamming distance ≤ 31.
- It fails on **crops and screenshot-of-screenshot**. For those: OCR → text fingerprint, or CLIP embedding cosine ≥ 0.9.
- In Postgres, `bit(256)` + `bit_count(a # b)` (PG14+) gives Hamming distance. A linear scan is fine per trace.

### Dating (`lineage/dating.py`)
| Kind | Example | Trust |
|---|---|---|
| platform | Bluesky `createdAt`, tweet snowflake, newspaper issue date | 3 |
| archive | first Wayback capture of the URL | 2 |
| metadata | `article:published_time`, JSON-LD `datePublished` | 1 |
| search | the date a search engine shows | 0 |

`best_date` = earliest date within the highest tier present. Known limitation (marked `ponytail:` in code):
an honest metadata date earlier than the first archive capture gets ignored.

**Snowflake:** `ms = (id >> 22) + 1288834974657` (Twitter/X), epoch `1420070400000` for Discord. Twitter IDs from before
Nov 2010 are sequential, not snowflakes; `snowflake_time` would give nonsense for them, so check `id > 2**40` first.

### Lineage tree (`lineage/tree.py`)
Greedy: sort by date. For each variant, the parent is the most similar *strictly earlier* variant with similarity ≥ threshold
(0.25). Anything else becomes a root. O(n²) similarity calls, which is fine up to a few thousand candidates.

Why greedy and not a maximum spanning arborescence (Chu-Liu/Edmonds)? Time already orders the graph (a parent must be
earlier), and with that constraint picking each node's best earlier parent independently *is* the optimal
arborescence. Edmonds only matters without the time constraint.

Root semantics: the oldest root is the "origin (earliest found)". A later root means an independent origin **or** a
missing link, and the UI draws it with a dashed "gap" connector to the nearest similar earlier node below the threshold.

### Diffs and labels
`diff_words` = `difflib.SequenceMatcher` over whitespace tokens → `[{op, old, new}]`. The LLM gets the parent, child, and
diff, and returns labels from a fixed enum (see PLAN Phase 2). The LLM never creates candidates or dates.

## Data model
See `schema.sql`. Key points:
- `candidates.parent_id` stores the tree; `changes` (jsonb) is the diff vs the parent; `labels` holds the LLM labels.
- `traces.sources` lists what was searched, shown to users as coverage.
- `http_cache.key = f"{source}:{sha1(normalized_request)}"`. The TTL is per source (Wayback: forever; search: 7 days).

## API

| Method | Path | Body / result |
|---|---|---|
| POST | `/api/tree` | `{variants:[{text,date,url}], threshold?}` → nodes (**exists**; used for manual/debug) |
| POST | `/api/traces` | `{text}` or multipart `image` → `{id}` |
| GET | `/api/traces/{id}` | `{trace, nodes:[{id,url,source,snippet,date,date_kind,parent,similarity,changes,labels}]}` |
| GET | `/api/traces/{id}/events` | SSE stream: `source_started`, `candidate_found`, `tree_updated`, `done`, `error` |
| GET | `/t/{id}` | share page (server-rendered OG tags) |

## Security / abuse
- Validate uploads (type sniffing, 10 MB cap). Never fetch user-supplied URLs pointing at private IP ranges (SSRF).
- Escape all snippet text in the UI (it's attacker-controlled web content).
- Per-IP trace rate limit (e.g. 10/hour) because every trace costs money.
