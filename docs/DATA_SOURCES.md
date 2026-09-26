# lineage: data sources

Verify limits and prices on each provider's site before you depend on them; these change.

## Discovery (finds candidates)

| Source | Endpoint | Auth / cost | Notes |
|---|---|---|---|
| SerpAPI (Google) | `GET https://serpapi.com/search.json?engine=google&q=...&tbs=cdr:1,cd_max:12/31/2015` | key; ~$75/mo for 5k | Date filter is what enables the "walk backward in time" search. |
| Brave Search API | `GET https://api.search.brave.com/res/v1/web/search?q=...` | key; has a free/cheap tier | Independent index, a good second opinion to Google. |
| Chronicling America (LOC) | `https://chroniclingamerica.loc.gov/search/pages/results/?andtext=&phrasetext=...&format=json&date1=1770&date2=1963&dateFilterType=yearRange` | free | OCR newspaper pages 1770–1963. OCR is noisy, so match with a low threshold. LOC is migrating this to loc.gov. If it moves, use `https://www.loc.gov/collections/chronicling-america/?q=...&fo=json`. |
| Google Books | `GET https://www.googleapis.com/books/v1/volumes?q="exact phrase"` | key optional | `publishedDate` = metadata tier; `searchInfo.textSnippet` = snippet. |
| Internet Archive | `GET https://archive.org/advancedsearch.php?q=...&output=json` (metadata) and the full-text search UI's API | free | Full-text search covers scanned books. |
| HathiTrust | full-text search (web) | free | No clean JSON API for full text. Use it for manual verification of ground-truth cases. |
| Google Fact Check Tools | `GET https://factchecktools.googleapis.com/v1alpha1/claims:search?query=...&key=` | free key | Returns ClaimReview items. Show them as a banner. |
| GDELT DOC 2.0 | `GET https://api.gdeltproject.org/api/v2/doc/doc?query="..."&mode=artlist&format=json&startdatetime=...` | free | News since 2017; `mode=timelinevol` gives a spread chart. |
| Media Cloud | API | free account | Alternative news archive. |
| Bluesky | `GET https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=...` | free (auth may be required for search, so check) | `createdAt` = platform tier. |
| Reddit | OAuth "script" app → `/search?q=...` | free at low volume | Old data: Arctic Shift dumps (Pushshift is gone). |
| Mastodon | `/api/v2/search?q=...&type=statuses` per instance | free | Full-text search is opt-in, so coverage is patchy. |
| Telegram | Telethon `client.iter_messages(channel, search=...)` | free (a phone-number account) | Public channels only. |
| YouTube Data API | `search.list?q=...&publishedBefore=` | free quota | Titles/descriptions only. |
| X / Twitter | official API | **$$$** (full-archive search needs a high tier) | Out of scope. Rely on snowflake decoding of screenshots + Wayback captures of tweet URLs. |

## Images (Phase 3)

| Source | Notes |
|---|---|
| TinEye API | Paid (~$200 / 5k searches). Supports `sort=crawl_date&order=asc`, which gives the oldest copies first. |
| SerpAPI `engine=google_lens` | Reverse image via Google Lens. |
| Yandex (via SerpAPI) | Strong for faces and Eastern European / Russian web. |
| Bing Visual Search | **Retired in 2025.** Don't use. |

## Dating (dates known URLs)

| Source | Endpoint | Notes |
|---|---|---|
| Wayback CDX | `GET https://web.archive.org/cdx/search/cdx?url=URL&output=json&limit=1&fl=timestamp&filter=statuscode:200` | Oldest-first by default. **URL-keyed, not content-searchable.** ~1 req/s politely; cache forever. |
| Memento TimeTravel | `GET http://timetravel.mementoweb.org/api/json/1990/URL` | Aggregates many archives (archive.today, national libraries). |
| Page metadata | `<meta property="article:published_time">`, JSON-LD `datePublished`, `<time datetime>` | Self-reported (metadata tier). |

## LLM

| Use | Model | Notes |
|---|---|---|
| Query generation, edge labels | `claude-sonnet-5` | JSON output; validate against a schema; never trust it for URLs/dates. |
| Screenshot OCR + field extraction | `claude-sonnet-5` (vision) | Returns `{platform, handle, displayed_date, post_id, text}`. |
| Cheap bulk relevance filtering (optional) | `claude-haiku-4-5-20251001` | Only if Jaccard/embeddings aren't enough. |

## Ground truth (for evals, not the product)
- Quote Investigator (quoteinvestigator.com): manually traced origins. **Don't scrape it**; read it by hand to build fixtures.
- Wikiquote "Misattributed" sections.
