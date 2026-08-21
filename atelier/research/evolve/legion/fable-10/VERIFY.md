# Fable-10 · R19 eval fixtures — verified

Verifier: one live `claude-fable-5-thinking-high` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `5e908ec` (Round 19).
Method: read `evalrun.py`, the four fixtures, the conductor, `DemoSpoke`,
`loom.demo_svg` and `store.update_brand_kit`; then drive every fixture through
a real `Conductor` on a throwaway `Memory` + temp artifacts dir — demo lane
only, no network, no key read, no paid call. Palette claims were checked
against the SVG *bytes on disk*, split into fill/stop-color attributes versus
the escaped caption text, because the two paths mean different things.

**Verdict: PASS, no code changes.** All five claims hold as shipped, so
`evalrun.py` is untouched. What the run exposed is not broken code but soft
truth: two of the four fixtures pass for reasons weaker than they look
(brief echo, not design application), one fixture does not pass the demo lane
at all, and the scorer has three lenient edges. All of it is now pinned as
current behaviour in `test_fable_10.py` rather than papered over.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `atelier/data/eval/` has four `brief_*.json`, each with `request` + `expected` | PASS — all four also carry both `must_mention` and `palette` |
| 2 | `load_fixture` / `list_fixtures` / `score_result` / `run_fixture` exist; `crafts_required` is not scored | PASS — a result satisfying zero graph keys still scores ok |
| 3 | `run_fixture` on `brief_logo.json` through a real demo `Conductor` returns `ok: true`, ≥1 artifact, kit hex in the SVG | PASS — and the logo hex is a *genuine* fill, not a caption echo |
| 4 | A missing `must_mention` makes `score_result` return `ok: false` | PASS — at score level and through a full mutated run |
| 5 | `Round19EvalFixtures.test_eval_briefs_load` still passes | PASS — inside the 51-test gate below |

## Path traced

`run_fixture(fixture, memory, conductor, artifacts_dir)` →
`memory.create_project(title, brand)` then, when the fixture ships a kit,
`memory.update_brand_kit` — which **rewrites the kit to
`{name, palette, voice}` via `brand_name`/`brand_colors` and drops `fonts`
on the floor** → `create_thread` → `conductor.run(provider="demo",
mode="fast")`:

- brand kit is re-read from the project; `palette` and `name` ride into
  every `image_spoke.image(...)` call.
- `DemoSpoke.chat` answers the planner with
  `intent = first-line-of-brief[:240]` and one weave item whose prompt is the
  full brief.
- `DemoSpoke.image` → `loom.demo_svg(prompt, title, palette)`:
  `brand_colors(palette)` maps kit swatches onto `bg` (colors[0]), `ink`
  (colors[1]), gradient stops — **and** bakes `html.escape(prompt[:180])`
  into a `<text>` caption.
- `write_bytes` puts the SVG at `artifacts_dir/<id>.svg`; the artifact row
  carries `path`, so `run_fixture`'s blob loop reads the real file (the
  `artifacts_dir / f"{id}.svg"` fallback never fires in this lane).
- summary message starts `Helix fast · {intent}`.

`score_result` then greps a haystack of `message` + `json.dumps(plan)` +
every artifact `prompt` for `must_mention` (case-insensitive), greps the raw
SVG bytes for `palette` hexes (case-sensitive, only when blobs exist), and
fails any artifact whose kind/mime contains a `lanes_forbidden` token.
`crafts_required`, `crafts_any_of`, `lanes_required`, `min_steps`,
`handoff_min`, `deliverable_kinds`, `content_terms` and `task_type` are never
read — they appear only in the module docstring, as documentation of the
research graph.

## Run evidence

All four fixtures through the real demo conductor, one fresh runtime each:

```
brief_logo.json        ok=True  artifacts=1  #1A5FB4  fill/stop=True  caption-echo=False
brief_poster.json      ok=True  artifacts=1  #101020/#39F2AE/#FF5DA2  fill/stop=False  caption-echo=True
brief_brand_kit_apply  ok=True  artifacts=1  #1A5FB4/#F5C211  fill/stop=True  caption-echo=True
brief_factsheet_…      ok=False artifacts=1  #0B3954/#E0A458  fill/stop=False caption-echo=False
```

Why each line reads the way it does — the offsets are the whole story
(`intent` truncates the brief at 240 chars, the SVG caption at 180):

```
logo:        '#1A5FB4' at 186 → past the 180 caption echo; the hit is the kit fill. Honest.
poster:      no brand kit; all three hexes sit at 124/150/162 → inside the caption echo. Echo-only.
brand_apply: 'Archivo' at 208, 'Inter' at 233 → inside the 240 intent; hexes at 89/106 → in the caption too.
factsheet:   no kit, hexes at 304/328 → past both echoes; nothing in demo can carry them. Fails.
```

The honesty probes, run against live modules:

- **brand_apply's Archivo/Inter hit is brief echo, not font application.**
  After `update_brand_kit` the stored kit is
  `{"name": "Atelier Helix", "palette": [...], "voice": ""}` — no `fonts`
  key survives. Scoring a result reduced to *message only* (no plan, no
  artifact prompts) still hits both needles, because the summary line embeds
  `intent = request[:240]`. Pinned in
  `test_brand_apply_mentions_ride_the_brief_not_the_kit`.
- **The kit→fill path is real, not another echo.** A synthetic fixture with
  palette `#ABCDEF`/`#123456` and a request that never mentions them scores
  `ok: true` with `fill="#ABCDEF"` in the SVG bytes; the identical fixture
  *without* the kit scores `ok: false`. The palette gate is live when blobs
  exist. Pinned in `test_kit_palette_lands_as_fill_without_brief_echo`.
- **The scorer can fail (claim 4), both ways.** Score-level: a result of
  `{"message": "nope"}` misses. Run-level: `brief_logo.json` mutated to
  require "Zanzibar Chrome Whale" comes back `ok: false` from a real demo
  weave. Pinned in `test_mutated_must_mention_fails_through_a_real_run`.

## Checked and *not* a hole

- **`list_fixtures` is prefix-strict**: a `notes.json` file and a
  `brief_dir.json` *directory* in the folder are both ignored.
- **`load_fixture` rejects** a fixture missing `request` or `expected` with
  `ValueError`, not a KeyError downstream.
- **`lanes_forbidden` bites**: an artifact of kind `video` fails the score.
- **No paid path**: `provider="demo"` is hardwired in `run_fixture`; the
  demo spoke never touches the keyring or the network.

## Folded after this note (conductor close)

No further scorer. Echo-vs-kit honesty stays pinned in the tests.

## Remaining holes (none blocking, all pinned as current behaviour)

1. **`brief_factsheet_legal_directory.json` cannot pass the demo lane.** It
   ships no brand kit and its hexes sit past both echoes, so `ok: false` is
   the honest demo verdict. It is a fixture for the richer graph (its
   `content_terms` — sample directory entries — are not scored either).
   Pinned in `test_all_four_fixtures_current_demo_truth`.
2. **Poster's palette pass is caption echo.** Legible from three metres it is
   not — the hexes are in the escaped `<text>` caption because the brief
   mentions them inside its first 180 chars, never as fill/stop-color.
   Pinned in `test_poster_palette_hits_only_via_prompt_echo`.
3. **Palette gate is skipped when no blobs are collected** (`if
   expected.get("palette") and blobs`), so a run whose artifacts vanish from
   disk can still score `ok: true` with every palette row a miss. Pinned in
   `test_palette_gate_skipped_without_blobs`.
4. **Hex matching is byte-exact and case-sensitive**: expected `#abcdef`
   misses `fill="#ABCDEF"`. Today's fixtures and `demo_svg` share casing, so
   nothing fails; a lowercase fixture would silently miss. Pinned in
   `test_palette_hex_match_is_case_sensitive`.
5. **The scorer never gates on `artifact_count`** — zero artifacts with a
   satisfied `must_mention` is `ok: true`; only the fable test asserts
   `artifact_count >= 1` on top. Pinned in
   `test_zero_artifacts_can_still_pass`.
6. **Both mention echoes are truncation-fragile**: `intent` cuts at 240
   chars and the caption at 180, so a `must_mention` needle past those
   offsets in a kit-less fixture can only hit via the artifact prompt.
   Documented here; offsets asserted in the brand_apply and logo tests.

None of these fail a claim, so `evalrun.py` ships unchanged — the leniencies
are the demo lane being honest about what it is, and the fixtures keep their
research-graph keys for the day a scorer reads them.

## Tests

`atelier/tests/evolve/test_fable_10.py` — was 3 tests; now 15. New:
`FixturesLoad` gains reject-missing-keys and prefix-strictness;
`ScorerSemantics` pins graph-keys-not-scored, forbidden lanes, the skipped
palette gate, hex case-sensitivity and the zero-artifact pass;
`DemoConductorRuns` runs all four fixtures (with the factsheet failure
pinned), proves the logo hit is a fill beyond the caption echo, proves
brand_apply's mentions ride the brief, proves kit→fill with a hex the brief
never says, and fails a mutated must_mention through a real run.
`Round19EvalFixtures` in `atelier/tests/test_evolve.py` passes untouched.

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_fable_10
Ran 51 tests — OK
```

Full tree (`unittest discover -s atelier/tests`): 365 tests, OK
(1 expected failure, pre-existing).
