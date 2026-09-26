# lineage: agent guide

"git blame for the internet": trace a claim's earliest found appearance and its mutations as a tree.

## Read first
1. `docs/PLAN.md`: phases with checkboxes. **Work on the first unticked task.** Tick boxes as you finish.
2. `docs/ARCHITECTURE.md`: pipeline, algorithms, and why they were chosen.
3. `docs/DATA_SOURCES.md`: endpoints, costs, limits.
4. `docs/DESIGN.md`: **the UI spec. The bar is striking and not AI-looking**, matching the author's portfolio/tidewatch/afterglow.

## Commands
```bash
python -m venv .venv && . .venv/Scripts/activate && pip install -e ".[dev]"
pytest -q
uvicorn lineage.api:app --reload      # http://localhost:8000
docker compose up -d                  # Postgres+pgvector, Redis (Phase 1+)
```

## Layout
- `lineage/fingerprint.py`: normalize, shingles (k=2), Jaccard
- `lineage/dating.py`: snowflake decode, date trust tiers, `best_date`
- `lineage/tree.py`: `build_tree` (greedy earliest-most-similar parent), `diff_words`
- `lineage/wayback.py`: earliest Wayback capture for a URL
- `lineage/api.py`: FastAPI; `POST /api/tree` today
- `lineage/sources/*.py`: (Phase 1) one module per source, `search(query, before) -> list[Candidate]`
- `web/`: Phase 0 static page; becomes Vite + TypeScript + custom SVG in Phase 0.5 (spec: docs/DESIGN.md)
- `schema.sql`: Postgres schema (auto-loaded by docker compose)

## Rules
- Keep it small: stdlib and existing deps first. A new dependency needs a reason in the commit message.
- The LLM writes **queries and labels only**. Candidates and dates must come from real fetched data.
- Every external HTTP call goes through the `http_cache`. Tests never hit the network (use canned responses in `tests/fixtures/`).
- Say "earliest found", never "earliest". Label posts, not people.
- Store snippets, not full pages.
- Non-trivial logic gets one focused test in `tests/`.
- UI work follows docs/DESIGN.md exactly: tokens only (no raw hex in components), self-hosted fonts, AA contrast, keyboard, and
  reduced motion. Check the result in the browser at 390 and 1440 and review it against the anti-"AI look" list before ticking.
- Secrets live in `.env` (see `.env.example`), never committed.
- Commit after each ticked task with a clear message; push to `origin main`.
