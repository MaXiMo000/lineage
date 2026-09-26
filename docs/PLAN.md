# lineage: build plan

Each phase ends with something demo-able. Tick the boxes as you go; a session picking up this repo
starts at the first unticked task.

## Product in one line

Input: a claim (text, URL, or screenshot). Output: a shareable **lineage tree** showing the earliest *found*
appearance, every variant, the date and date-confidence for each, and a labelled diff for each mutation.

## Non-negotiables (apply to every phase)

- Say **"earliest found"**, never "earliest". Always list which sources were searched.
- Label **posts**, never people ("this post introduced the Einstein attribution", not "X is the liar").
- Store **snippets + links + hashes**, never full pages or images.
- **Cache every external call** (`http_cache` table). Archives rate-limit; search APIs cost money.
- Every date carries its kind: `platform > archive > metadata > search` (see `lineage/dating.py`).

---

## Phase 0: Scaffold + ground truth (done: scaffold · todo: test set)

- [x] Core algorithms: normalize/shingle/Jaccard, snowflake decode, date trust tiers, greedy tree, word diff
- [x] `POST /api/tree` + a minimal page that renders a tree from manually entered variants
- [x] `schema.sql`, docker compose (pgvector + redis)
- [ ] **Ground-truth test set** in `tests/fixtures/cases/*.json`: 5 famous misattributed quotes, traced by hand
      using Quote Investigator / Wikiquote "misattributed" sections. Each case: the input claim, the expected
      earliest source (+ year), and 4–10 expected variants with years. Suggested cases:
      1. "Not everything that counts can be counted" (Einstein → W. B. Cameron, 1963)
      2. "Be the change you wish to see in the world" (Gandhi paraphrase)
      3. "The definition of insanity is doing the same thing over and over…" (Einstein → Narcotics Anonymous, 1981)
      4. "Well-behaved women seldom make history" (Laurel Thatcher Ulrich, 1976)
      5. "If I had asked people what they wanted, they would have said faster horses" (Ford, earliest ~1999)
- [ ] `scripts/eval.py`: runs the pipeline on every case. Reports **earliest-year error** and **variant recall**.
      This is the number you optimise for the rest of the project.

**Acceptance:** `python scripts/eval.py` prints a table, even if Phase 1 isn't built (0 recall).

---

## Phase 0.5: Design foundation (1–2 weeks). **The UI must be striking, not AI-looking.**

Read `docs/DESIGN.md` first; it's the spec. Build against the ground-truth fixtures through `POST /api/tree`, so the
design is judged on real data before retrieval exists.

- [ ] `web/` becomes **Vite + TypeScript** (no UI framework unless state gets hairy; the graph is custom SVG, **not** React Flow).
      FastAPI serves `web/dist` in production; Vite proxies `/api` in dev
- [ ] Tokens (`web/src/tokens.css`): the six colours with their measured contrast ratios in comments, a type scale, a 4px spacing grid,
      motion durations/easing, z-layers. Fonts self-hosted with `@fontsource/newsreader`, `ibm-plex-mono`, `instrument-sans`
- [ ] Hero / empty state per DESIGN.md §Screens 1, with sample-claim buttons wired to the fixtures
- [ ] Graph: a time axis with mono year ticks; lanes; square specimen nodes; orthogonal elbow edges; the EARLIEST FOUND stamp;
      dashed `--gap` missing-link connectors; hovering a node lights its ancestry path
- [ ] Specimen inspector with the inline proofreader diff (`--mutation` underline for insertions, struck `--graphite` for deletions),
      mutation tags, and the `●●●○` trust tier
- [ ] Commit-log view (`L`), keyboard map + `?` overlay, and focus rings
- [ ] Mobile: a vertical git graph + bottom-sheet inspector, verified at 360/390
- [ ] Screenshots at 390 and 1440 in `docs/screenshots/0.5/`, self-reviewed against the DESIGN.md anti-"AI look" list.
      Fix anything that fails before ticking

**Acceptance:** Lighthouse Accessibility 100 and Performance ≥ 90; no item on the anti-"AI look" list present; the 1440 screenshot
of the "Not everything that counts" tree reads as a poster.

---

## Phase 1: Text-quote MVP (2–3 weeks)

Goal: paste a quote and get a real tree for at least 3 of the 5 ground-truth cases, with no manual input.

### 1a. Persistence + jobs
- [ ] `lineage/db.py`: psycopg 3 connection pool; CRUD for `traces` / `candidates`; `http_cache` get/set helper
- [ ] `POST /api/traces {text}` → creates a trace, enqueues a job (RQ), returns `{id}`
- [ ] `GET /api/traces/{id}` → trace + candidates + tree
- [ ] `GET /api/traces/{id}/events` → Server-Sent Events: `source_started`, `candidate_found`, `dated`, `tree_updated`, `done`

### 1b. Query generation
- [ ] `lineage/queries.py`: Claude (`claude-sonnet-5`) turns the claim into 10–20 queries: the exact quote in quotes,
      the claim without its attribution, 2–3 distinctive 4–6 word fragments, likely paraphrases, a translation if the
      claim is in another language. Return JSON; validate it; cap the count.
- [ ] Unit test with a canned LLM response (no network in tests)

### 1c. Retrieval sources (one module each in `lineage/sources/`, same signature)
`def search(query: str, before: date | None) -> list[Candidate]`
- [ ] `serpapi.py`: Google results with `tbs=cdr:1,cd_max:MM/DD/YYYY`. **Walk backward in time**: search
      before today, take the oldest result year Y, search again with `before=Y`, and repeat until empty (max 5 hops)
- [ ] `chronam.py`: Chronicling America full-text (1770–1963 US newspapers). Free, and the best source for old quotes
- [ ] `books.py`: Google Books API `volumes?q="..."` (the published date is metadata-tier) + Internet Archive full-text search
- [ ] `factcheck.py`: Google Fact Check Tools `claims:search`. Show a banner, and don't add these to the tree
- [ ] Every source goes through the `http_cache`

### 1d. Dating
- [ ] For each web candidate: `wayback.earliest_capture(url)` (archive tier) + parse `article:published_time` /
      JSON-LD `datePublished` (metadata tier). Newspapers/books: the issue/publication date (platform tier; the
      archive vouches for it)
- [ ] `best_date()` picks the date; store `date_kind`

### 1e. Tree + UI
- [ ] Filter candidates: `similarity(claim, snippet) >= 0.2` or embedding cosine ≥ 0.75 (add `sentence-transformers`
      `all-MiniLM-L6-v2` only if recall on the eval set needs it)
- [ ] `build_tree()` over the surviving candidates
- [ ] Wire the Phase 0.5 UI to real traces: the hero input posts to `/api/traces`, and the result page loads `/api/traces/{id}`
- [ ] Live-updating tree over SSE: the "Tracing" screen in docs/DESIGN.md (truthful log, nodes appearing on the axis, edge traces, FLIP)
- [ ] Permalink `/t/{id}`

**Acceptance:** eval shows ≥3/5 cases with earliest-year error ≤ 5 years; a fresh trace finishes in < 2 min.

---

## Phase 2: Mutation labels + sharing (1–2 weeks)

- [ ] `lineage/labels.py`: for each edge, give Claude the parent, child, and word diff; it returns 1–3 labels from a fixed
      enum: `attribution_added | attribution_swap | attribution_removed | number_change | entity_swap |
      date_change | context_added | hedge_removed | exaggeration | translation | truncation`
- [ ] "Commit log" view: a vertical list, like `git log --oneline`: `1986  a1f3  attribution_removed  "…"`
- [ ] Open Graph image per trace (render with `@vercel/og` or Playwright screenshot of `/t/{id}?card=1`)
- [ ] "Download tree as PNG" button
- [ ] Report/correction form on each trace (stores to a `reports` table; no email yet)

---

## Phase 3: Screenshots + images (2 weeks)

- [ ] `POST /api/traces` accepts an image upload (limit 10 MB; store in local disk / R2)
- [ ] OCR: a vision call to Claude returns `{platform, handle, display_name, displayed_date, post_id?, text}`
- [ ] **Fake-screenshot check**: if `post_id` is visible, `snowflake_time(post_id)` vs `displayed_date`. Show a mismatch
      in red. Also check whether the handle exists / the post is archived on Wayback
- [ ] `lineage/imagehash.py`: PDQ via `pdqhash`; Hamming distance ≤ 31/256 = same image. Store it in `candidates.pdq`
- [ ] Reverse image sources: `tineye.py` (paid API, oldest-first sort available) and `lens.py` (SerpAPI google_lens)
- [ ] Image variants join the same tree; mark crops/re-encodes as `re-upload` edges

---

## Phase 4: Social spread (2–3 weeks)

- [ ] `bluesky.py`: `app.bsky.feed.searchPosts` (public AppView, free). Exact timestamps (platform tier)
- [ ] `reddit.py`: official API (OAuth "script" app, free at low volume). Historical data: Arctic Shift dumps
- [ ] `mastodon.py`: search on large instances (full-text search is opt-in per instance, so recall is patchy)
- [ ] `telegram.py`: Telethon over public channels only
- [ ] `gdelt.py`: GDELT DOC 2.0 API for news spread since 2017 (volume timeline chart under the tree)
- [ ] Spread chart: count of candidates per month per root

---

## Phase 5: Distribution (ongoing)

- [ ] Browser extension (MV3): right-click selected text or an image and choose "Trace with lineage"
- [ ] Public API with a key + rate limit
- [ ] Embeddable tree widget for fact-checkers' articles
- [ ] Rerun the eval set with every retrieval change; publish the numbers in the README

---

## Costs (MVP, rough)

| Item | Monthly |
|---|---|
| SerpAPI (5k searches) | ~$75 |
| VPS (2 vCPU, 4 GB) running API + worker + Postgres + Redis | ~$10–25 |
| Claude API (≈ 20 queries + labels per trace, ~$0.01–0.03/trace) | ~$10 at 500 traces |
| TinEye API (Phase 3) | from ~$200 per 5k searches, so gate it behind a daily cap |

## Risks

| Risk | Mitigation |
|---|---|
| The origin is in WhatsApp/Facebook/TikTok (unreachable) | Show "earliest found", the coverage list, and gap markers |
| Backdated page metadata | The trust tiers; archive beats metadata |
| Legal (defamation / copyright) | Label posts not people; snippets only; a correction form |
| API terms / costs | Official APIs only; no X scraping; cache; daily budget caps per source |
| An LLM hallucinating sources | The LLM only writes **queries** and **labels**. Every candidate must come from a real fetched URL |
