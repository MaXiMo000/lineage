# lineage: design

**This UI must be striking and must not look AI-generated.** It sits next to `portfolio`, `tidewatch`, and `afterglow`,
and shares their DNA: a dark ground, warm type, hairline edges, one reserved signal colour, mono for every number,
and loading as real progress, not a spinner. No 3D. The drama comes from **typography, a real time axis, and a tree that
grows while you watch**.

## Concept: a forensic commit graph

A rumor is shown like `git log --graph` under an evidence lamp. Time runs left → right on a real axis. Every variant is a
*specimen*: the words set in a newspaper serif, the evidence (source, date, trust) in mono. The only colour on the page
marks **what changed**: the mutated words. You should be able to screenshot any state and have it read as a poster.

## Palette (six tokens, each with one rule)

| Token | Value | Rule |
|---|---|---|
| `--ink` | `#0A0A0B` | ground |
| `--bone` | `#ECE7DC` | primary type, the selected lineage path |
| `--graphite` | `#9A958C` | secondary type, unselected edges, axis labels |
| `--hair` | `rgba(236,231,220,.08)` | every rule, panel edge, and unselected lane. Never brighter |
| `--mutation` | `#FF5B3A` | **changed words and mutation labels only.** Never a button, border, or decoration |
| `--gap` | `#6F6A62` | dashed "missing link" connectors and "earliest *found*" caveats |

Every text token must clear WCAG AA (4.5:1) on `--ink` by itself. Check with a contrast tool and write the ratios in `styles.css`.

## Type

- **Newsreader** (variable, optical-size axis): claims and quotes. Large optical size for the hero claim, small for specimen cards.
  Italic is reserved for the *claimed attribution* ("— Albert Einstein"), which is visually the suspect part.
- **IBM Plex Mono**: dates, URLs, hashes, trust tiers, counts, labels. `font-variant-numeric: tabular-nums`.
- **Instrument Sans**: UI controls and body copy.
- Self-host with `@fontsource/*` (npm, bundled, same origin, no Google Fonts CDN), as in tidewatch.

## Screens

### 1. Hero (empty state)
- The full viewport is `--ink`. One enormous serif question, left-aligned, e.g. *Where did this actually come from?*, with
  "actually" in italic.
- One input: a single line that grows into a textarea on paste, a mono placeholder, and "or drop a screenshot" as a quiet affordance.
- Below it: 4–5 famous claims as dashed-underline mono buttons (Einstein insanity, Gandhi change, Ford horses…). One click runs a real trace.
- Nothing else. No feature cards, no logos, no footer wall.

### 2. Tracing (loading is a scene)
- The input slides up into a thin top bar. The time axis draws in (hairline, year ticks in mono).
- A **truthful log** in mono at the bottom left, driven by the SSE events: `▸ chroniclingamerica  1770–1963 … 14 hits`,
  `✓ wayback  dated 31 urls`. Each line rises in (180 ms).
- Nodes appear **on the axis as they're found**, and edges draw with a `stroke-dashoffset` trace when the tree updates. The tree rearranges
  with FLIP transitions, never a jump. Watching it grow *is* the demo.

### 3. Result
- **Graph (left ~65%)**: x = date (a linear or log-ish scale, as long as it's labelled), y = lane per root/branch. Nodes are small
  squares (specimens), not circles. Edges are orthogonal "git graph" elbows. The earliest found node carries a mono stamp
  `EARLIEST FOUND · 1963`. Later roots connect to their nearest ancestor with a dashed `--gap` line labelled `missing link?`.
- **Specimen inspector (right ~35%, a bottom sheet on mobile)**: the claim in serif with an inline diff against its parent.
  Deleted words are struck through in `--graphite`; inserted words are `--bone` with a 2px `--mutation` underline; replaced words show both.
  Under it, the mutation labels as mono tags (`ATTRIBUTION_ADDED`) in `--mutation`, then the evidence block: source, URL,
  Wayback link, and date plus trust tier drawn as `●●●○` (platform/archive/metadata/search).
- **Commit-log toggle** (`L`): the same tree as `git log --oneline --graph` in mono, with a 7-character hash per variant. It's the
  nerd view, and it's genuinely useful for scanning.
- **Coverage strip** (bottom): which sources were searched and which couldn't be reached (WhatsApp, private Facebook).
  Honesty is part of the design.

### 4. Share card (Open Graph / PNG export)
A poster: the origin quote in large serif, the mutated final version beneath it with the changed words in `--mutation`, a mini
graph as a sparkline of nodes over time, and `lineage · earliest found 1963 · 23 variants`. 1200×630.

## Motion
- Durations 120–220 ms for UI and 400–700 ms for graph re-layout. One easing: `cubic-bezier(.2,.7,.2,1)`.
- Everything is interruptible. `prefers-reduced-motion` means no traces or FLIP, just instant state changes.
- Hovering a node lights its full ancestry path in `--bone` and dims everything else to `--hair`.

## Keyboard
`/` focus input · `←/→` previous/next node in time · `↑/↓` switch lane · `Enter` open inspector · `L` commit-log view ·
`S` share · `Esc` close · `?` help overlay. Every control has a visible focus ring (2px `--bone`, offset 3px).

## Layout
Verify at 360, 390, 768, 1024, 1440, and 1920 widths. On mobile the time axis runs **top → bottom** (a vertical git graph), and the inspector
is a bottom sheet. No horizontal page scroll, ever; the graph pans inside its own viewport. Dark theme only, by design (document this).

## Anti-"AI look" rules (a reviewer rejects any of these)
- No purple/blue gradients, gradient text, glows on everything, or glassmorphism card stacks.
- No "hero + three feature cards + CTA" layout. No emoji as icons, no ✨. No generic Tailwind `rounded-2xl shadow-lg` cards.
- No Inter-everywhere. No default React Flow / chart-library chrome. The graph is our own SVG.
- No skeleton shimmer. Loading shows real, truthful progress.
- No filler copy. Every sentence is specific ("Searched 7 archives, 1770–today"), and nothing is lorem ipsum or "Unlock insights".
- Icons: very few, custom SVG, 1.5px stroke, matching the hairline weight.

## Quality bar (definition of done for any UI task)
- WCAG AA contrast; full keyboard use; screen-reader labels (the graph has an equivalent `<ol>` of variants for AT).
- Lighthouse: Performance ≥ 90, Accessibility = 100, Best Practices = 100 on the result page.
- No layout shift when nodes stream in (reserve the space).
- Screenshots at 390 and 1440 wide are saved to `docs/screenshots/<milestone>/` and compared against this doc before ticking the task.
