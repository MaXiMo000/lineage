# lineage

**`git blame` for the internet.** Paste a viral claim, quote, or screenshot. lineage finds the earliest
known appearance, then shows how the claim mutated as it spread, like a commit history for a rumor.

```
1963  "Not everything that can be counted counts, and not everything that counts can be counted."
      (W. B. Cameron, Informal Sociology)
  └─ 1980s  "...not everything that counts can be counted"              (clauses reordered, source dropped)
       └─ 2000s  "...not everything that counts can be counted." — Albert Einstein   ← attribution_added
            └─ 2010s  same text on thousands of quote images            ← image fan-out
```

> Status: **scaffold / Phase 0.** The core algorithms (fingerprinting, dating, lineage tree, word diffs) work
> and have tests. Retrieval, persistence, and the real UI are the next phases. See [docs/PLAN.md](docs/PLAN.md).

## How it works (one paragraph)

Archives like the Wayback Machine are indexed by **URL, not content**, so lineage *discovers* candidates via
search engines, newspaper/book archives, and open social APIs, and then *dates* them with archive captures and
platform timestamps. Candidates get text-fingerprinted (shingles → Jaccard/MinHash) and image-hashed (PDQ).
They're ordered in time, and each variant is attached to its most similar earlier variant. Word-level diffs between
parent and child are the "commits", and an LLM labels them (attribution swap, number change, …).

## Run it

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate elsewhere
pip install -e ".[dev]"
pytest
uvicorn lineage.api:app --reload                  # http://localhost:8000
```

`docker compose up -d` starts Postgres (pgvector) and Redis for Phase 1+.

## Docs

- [docs/PLAN.md](docs/PLAN.md): phases, tasks, acceptance criteria
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): pipeline, data model, algorithms, API
- [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md): every source, endpoint, limit, cost, and license
- [docs/KICKOFF.md](docs/KICKOFF.md): the prompt to start a new Claude Code session on this repo

## License

MIT
