# Opus-04 — Round 8 (4-up variants) verification

**Verdict: PASS.** `variants=4` produces four distinct artifacts, four board nodes in a
2×2 block, and a quote that prices all four *before* the weave. The round's claim in
`ROUNDS.md` (`variants=4` / "four variants" → 2×2) holds on the live tree. Holes below
are real but none of them falsify the round.

Scope: read-only over `atelier/helix/conductor.py`, `atelier/server.py`, `atelier/web/*`.
No live file under those paths was edited. Tests live in `atelier/tests/evolve/test_opus_04.py`.

## Path traced

| Step | Where | Behaviour |
|---|---|---|
| Checkbox | `web/index.html` | `<input type="checkbox" id="variants"> 4-up variants` |
| Payload | `web/app.js`, `runBody()` | `variants: checked ? 4 : 0`, shared by Quote and Run |
| Route | `server.py`, `/api/threads/:id/run` | `variants=int(body.get("variants") or 0)` → `Conductor.run` |
| Quote route | `server.py`, `/api/quote` | `count = count or variants or 1`, clamped to 4 in `quote_run` |
| Intent | `conductor.py`, `_wants_variants` | explicit count clamped to `[2, 4]`; else prompt phrases → 4; else 0 |
| Pre-spend | `conductor.py`, `Conductor.run` | `quote_run(count=_wants_variants(...) or 1)` — 4 images quoted, budget checked first |
| Fan-out | `conductor.py`, `Conductor.run` | weave replaced by N items, prompt suffixed `— variant i`, `plan["variants"] = N` |
| Layout | `conductor.py`, `next_board_offset` | `grid = 2` when `n_variants >= 2` → 2×2 |
| Summary | `conductor.py`, `_summarize` | `Variants: 4` line on the assistant message |

(Symbols, not line numbers: the live tree is moving under other legion agents.)

## Four artifacts confirmed (demo lane)

In-process and over real HTTP (`POST /api/threads/:id/run`, `provider=demo`, `variants=4`)
on a fresh project: 4 rows in `artifacts`, 4 SVG files written under the artifacts dir
(700 bytes each, all four byte-distinct, prompts ending `variant 1..4`), 4 image nodes at
exactly `(72,72) (432,72) (72,352) (432,352)`, `plan.variants == 4`,
`plan.quote.count == 4`, phases `brief → score → route → weave → pin → done`, and each
`GET /api/artifacts/:id` returns 200 with a non-empty body. Prompt-only trigger
("four variants of a navy mark", no `variants` field) reaches the same result.
`variants=9` is capped at 4; unchecked box (`variants=0`) still pins exactly 1.

Fail-closed still holds under fan-out: with a paid lane whose image call always raises,
all four variants fail and the run raises `ConductorError` with zero artifacts minted —
no demo SVG smuggled into a paid 4-up.

## Remaining holes

**H1 — No pick-winner API, and no variant-set identity.** This is the biggest gap. The
four artifacts share nothing that marks them as siblings: `parent_id` is `NULL`, node
`meta` is `{}`, and `plan["variants"]` is only a count. There is no route to promote a
winner (`server.py` has no `winner` / `pick` / `promote` path), no way to cull the other
three except four `undo`s in reverse order, and no way to say "iterate on #3". The web
board has no selection affordance either — a node's only tool is Download, and
`state.lastArtifactId` is set in `renderBoard` to whichever image node happened to render
last, so a follow-up "spot edit this" after a 4-up targets an arbitrary variant rather
than a chosen one. Smallest honest fix: a `variant_set` id (or reuse `parent_id`) stamped on the four
artifacts plus `POST /api/artifacts/:id/pick` that flags the winner and deletes or dims
its siblings' nodes; the board then needs a click-to-select state feeding
`parent_artifact_id`.

**H2 — The 2×2 is only a 2×2 on an empty board.** `next_board_offset` counts *all*
existing nodes, so a 4-up on a board that already holds an odd number of nodes straddles
three rows instead of forming a block (verified: 1 pre-existing note → the four variants
occupy 3 distinct `y` values). Worse, earlier nodes were placed with `grid=3` while the
4-up uses `grid=2`, so the two lattices interleave and a second 4-up never visually reads
as a set. Fix shape: lay variants out relative to a set origin rather than the global node
count.

**H3 — Partial paid failure silently degrades a 4-up.** When some variants fail on a paid
lane, surviving images compact onto the first cells (verified: 2 of 4 → both on row 0)
while `plan["variants"]` still says 4 and the summary reads "Pinned 2 artifact(s)" next to
"Variants: 4". The UI shows only `errors[0]`, so a user who paid for and received two
images sees a board that looks like a deliberate 2-up.

**H4 — Intent match is a bare substring.** `"no variants please, just one"` returns 4, as
does any brief that merely mentions variants or 变体. There is no negation handling and no
way to express "one only" in prose once the word appears.

**H5 — `variants` is never validated.** Non-numeric input crashes the `int()` call:
`POST /api/threads/:id/run` answers 500 (`invalid literal for int()`) rather than 400, and
`POST /api/quote` is worse — its `int()` sits outside any `try`, so the handler raises, no
response is written, and the client sees a dropped connection. The
live contract advertises 400 for invalid input. Negative values degrade harmlessly to 1.

**H6 — Variants are not actually varied.** The only diversity signal sent to the provider
is the `— variant i` prompt suffix; there is no seed, temperature, or direction axis. Demo
SVGs differ only because `demo_svg` derives `c2` from a hash of the prompt when the brand
palette has fewer than four colours — an accident, and an off-palette one. On a real paid
lane the same brief can return four near-identical images while the quote bills for four.

**H7 — Fan-out discards the planner's board.** When variants are on, `weave_items` is
rebuilt from `weave[0]` alone, so a brief that legitimately asked for four *different*
assets collapses into four takes of the first. Conversely `variants` is ignored when the
planner already emitted 4 items with `count: 2` each — that path can pin 8 artifacts while
the quote priced at most 4.

## Repro

```bash
cd <repo> && python3 -m unittest atelier.tests.evolve.test_opus_04   # 22 tests, OK
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve  # gate: 28 tests, OK
```

Release gate re-run after adding this agent's tests: 47 tests, OK.
