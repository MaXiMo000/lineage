# Session kickoff prompt

Paste this into a fresh Claude Code session opened in this repo's folder:

---

You're picking up **lineage**, "git blame for the internet". Paste a viral claim/quote/screenshot, and it finds the
earliest *found* appearance and shows how the claim mutated as it spread, as a shareable lineage tree.

1. Read `CLAUDE.md`, then `docs/PLAN.md`, `docs/ARCHITECTURE.md`, `docs/DATA_SOURCES.md` in full before writing code.
2. Run `pip install -e ".[dev]" && pytest -q` to confirm the baseline is green.
3. Find the first unticked task in `docs/PLAN.md`. Work through tasks **in order**, one at a time:
   - implement the smallest version that meets the task, following the rules in CLAUDE.md
   - add or extend one focused test; `pytest -q` must stay green
   - tick the box in PLAN.md, commit with a descriptive message, `git push`
4. For the Phase 0 ground-truth cases, research each quote's real origin (use web search; cross-check Wikiquote and
   Quote Investigator by reading them, not scraping). Record sources in each fixture so every expected year is verifiable.
5. Before starting any task that needs an API key (SerpAPI, Brave, TinEye, Anthropic, Fact Check), check `.env`. If the
   key is missing, ask me for it and meanwhile build that module against canned fixtures.
6. At the end of each phase: run `scripts/eval.py`, paste the results table into the README "Status" section, and
   summarise for me what's done, the eval numbers, and what's next.

Guardrails: no scraping X/Twitter, no storing full pages, the LLM never invents candidates or dates, and always say
"earliest found". If a design decision in the docs turns out wrong, update the doc in the same commit and tell me why.

Start now with Phase 0 → "Ground-truth test set".
