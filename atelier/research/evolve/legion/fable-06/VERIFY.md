# Fable-06 · R11 spot-edit / board selection — VERIFIED

Verdict: **PASS** (with one small selection-binding fix applied by the verifier).

Verified at commit `8c46bc0` ("Round 11: select a board card as the next weave
parent") on branch `cursor/atelier-byok-studio-d639`, by reading the live tree
and exercising a real HTTP server on the demo provider. No paid calls.

## Claims checked

1. **Conductor stores `parent_id` / `plan.spot_edit`** — PASS.
   `atelier/helix/conductor.py` resolves `parent_artifact_id` via
   `memory.get_artifact(...)`; when found it sets
   `plan["spot_edit"] = {"parent_id": ...}` and every woven artifact row gets
   `parent_id=parent["id"]` (`memory.add_artifact`, column added by migration
   in `atelier/helix/store.py`). An unknown id is ignored, not fatal.
2. **Board selection** — PASS. In `atelier/web/app.js`, both the card `click`
   handler and the "Use as reference" button set `state.selectedArtifactId`
   and `state.lastArtifactId`, then `refreshBoard()` re-renders; selected
   cards get the `selected` class and `.node.selected` is styled in
   `atelier/web/styles.css` (accent border + ring). The button label flips to
   "Reference" while selected.
3. **`runBody()` parent priority** — PASS.
   `parent = state.selectedArtifactId || (spotWords ? state.lastArtifactId :
   undefined) || state.lastUploadId || undefined`, sent as
   `parent_artifact_id`. Selection wins without magic words.
4. **Spot words** — PASS. Regex is
   `/spot|局部|edit this|refine|larger type|bigger type/i`.
5. **Tests** — PASS. `atelier.tests.evolve.test_fable_06` and
   `Round06to12Board.test_spot_edit_sets_parent` (in
   `atelier/tests/test_evolve.py`) both exist and pass.

## Live HTTP evidence (demo provider, real server)

Booted `python3 -m atelier` (port 8794), then:

- `POST /api/projects` → project; `POST .../threads` → thread.
- `POST /api/threads/<t>/run {"prompt":"base mark","provider":"demo"}` →
  parent artifact `21bd3a84…`.
- `POST /api/threads/<t>/run {"prompt":"make the type larger","provider":
  "demo","parent_artifact_id":"21bd3a84…"}` → child `artifacts[0].parent_id ==
  21bd3a84…` and `plan.spot_edit == {"parent_id":"21bd3a84…"}`.
- Served `/web/app.js` contains the selection wiring (7 hits of
  `selectedArtifactId`), so the running server serves the fixed file.

## Fix applied by verifier (selection binding)

Switching to another project (or creating a new one) reset `lastUploadId`
but **not** `selectedArtifactId` / `lastArtifactId`, so a card selected in
project A silently became the `parent_artifact_id` for the next weave in
project B (the conductor's `get_artifact` is not project-scoped, so the
cross-project parent would be accepted and stored). `app.js` now nulls
`selectedArtifactId` and `lastArtifactId` in both project-switch paths.
Pinned by `SpotWiring.test_selection_clears_when_the_project_changes`.

## Tests run

`python3 -m unittest atelier.tests.evolve.test_fable_06 atelier.tests.test_helix
atelier.tests.test_evolve` — 40 tests, OK. Also
`atelier.tests.evolve.test_fable_03` (touched by the R11 commit) — 13 tests,
OK. New tests added: runBody priority-order regex pin, spot-word list pin,
selection-clear pin, unknown-parent tolerated over HTTP, `spot_artifact_id`
alias over HTTP.

## Remaining holes to fold before closing R11

- **Conductor does not scope the parent to the project/thread.** Any valid
  artifact id from any project is accepted as parent (`get_artifact` has no
  project filter). The UI leak is fixed, but a raw API caller can still
  cross-link projects. One-line guard in `conductor.run` would close it.
- **Selection can point at a deleted board node.** Deleting the selected
  card leaves `selectedArtifactId` set; the artifact row usually survives so
  the next weave still parents on it. Harmless but surprising; clear
  selection on delete or when the id vanishes from the board.
- **Selection persists across weaves by design** — after a spot edit, the old
  parent stays selected, so repeated runs keep the same parent rather than
  chaining onto the newest child. Fine for iterating on one source; worth a
  deliberate call in a later round.
- Wiring assertions in `test_fable_06.SpotWiring` are text/regex pins on
  `app.js`, not DOM execution (stdlib-only, no JS runtime). The HTTP layer is
  exercised for real; the click→state path is pinned but not executed.
