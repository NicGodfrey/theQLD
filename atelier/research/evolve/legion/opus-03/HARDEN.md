# Opus-03 — Round 6 (canvas camera) verification

**Verdict: PASS**, with two real holes found and folded on this branch. Every
claim in the round was checked by running it: the store through `Memory`
directly, the routes over real HTTP against a live `ThreadingHTTPServer`, and
`atelier/web/app.js` itself executed under node against that same server via a
DOM shim, so Home / Fit / the debounce are proven by clicking them rather than
by grepping for their names. Demo lane only — no provider key was configured
and no paid call was made. This supersedes the conductor-fill note that stood
on this page.

The two holes were **not** cosmetic. One let a single camera write make
`/api/projects` unparseable in the browser for *every* project; the other
silently threw away a pan whenever you switched projects just after making it.
Both are fixed here and both are pinned by tests that fail against `91cf452`.

Scope: `atelier/helix/store.py` (`set_camera`), `atelier/server.py`
(camera + board routes), `atelier/web/app.js`, `atelier/web/index.html`,
`atelier/web/styles.css`. Tests in `atelier/tests/evolve/test_opus_03.py`, plus
one gate assertion in `test_evolve.Round06to12Board.test_camera_persist`.

## Path traced

| Step | Where | Behaviour |
|---|---|---|
| Column | `store.SCHEMA` + `_migrate` | `projects.camera TEXT NOT NULL DEFAULT '{"x":0,"y":0,"zoom":1}'`, back-filled by `ALTER TABLE` on old DBs |
| Hydrate | `store._hydrate_project` | JSON-decodes `camera` on every project read, so list / get / board agree |
| Write | `store.set_camera` | non-dict → `{}`; each axis `float()` with a fallback; `zoom<=0 → 1`; `min(3, max(0.25, zoom))`; **now** any non-finite result falls back too |
| Route (write) | `server.py` `POST /api/projects/:id/camera` | body `camera` key, else the body itself; `set_camera` returns `None` for an unknown id → `404 missing project` |
| Route (read) | `server.py` `GET /api/projects/:id/camera` | `404 missing project`, else `{"camera": …}` |
| Route (board) | `server.py` `GET /api/projects/:id/board` | `{"nodes": …, "camera": …}` |
| Apply | `app.js applyCamera` | `translate(x,y) scale(z)` on `#board`, which is `transform-origin: 0 0` in `styles.css` — the Fit maths below depends on that |
| Zoom | `app.js` wheel handler | `0.92` / `1.08` per tick through `clampCamera` |
| Pan | `app.js` pointer handlers on `#boardWrap` | skipped when the target is inside `.node` or `.board-tools`, so the camera buttons stay clickable |
| Drag | `app.js enableDrag` | `node.x = ox + (clientX - sx) / zoom` — screen delta divided by zoom |
| Home | `#camHome`, `#camReadout` | `resetCamera()` → `{0,0,1}` |
| Fit | `#camFit` | `fitCamera()` over `#board .node`, 64 px padding, clamped to the same 0.25–3 band; empty board falls back to `resetCamera()` |
| Persist | `app.js persistCamera` | 180 ms debounce; **now** captures `{projectId, camera}` when scheduled, flushes on `pagehide` and before a project switch; errors still swallowed |

## Live evidence

**Routes.** Fresh runtime per test. `POST {"camera":{"x":40,"y":-12,"zoom":1.5}}`
returns the hydrated project; `GET .../camera`, `GET .../board` and the entry in
`GET /api/projects` all agree on `{40.0, -12.0, 1.5}`, and the value survives
closing the SQLite handle and reopening the file. `zoom` 99 → `3.0`, `0.01` →
`0.25`, `0` / negative → `1.0`, `"2.5"` → `2.5`, and `"abc"` / `None` / a list /
a dict / a bare object → the home camera instead of a 500. `{"camera": {}}`,
`{"camera": "nope"}`, `{"camera": [1,2]}` and a body-less POST all land on
`{0,0,1}`; a malformed body is `400 invalid json`. Both `POST` and `GET` on an
unknown project id are `404 {"error": "missing project"}`.

**Board (real `app.js` under node, real HTTP).** Booting against a project with
two cards at `(100,100,300×200)` and `(900,600,300×200)` in a 1000×800 viewport:
30 wheel-in ticks show `300%` in the readout and `scale(3)` on the board, issue
**0** writes during the burst and exactly **1** after it — the debounce works —
and the server then holds `{0,0,3}`. `Fit` writes once and the server holds
`zoom 0.792727`, `x -15.2727`, `y 43.2727`, which is exactly
`min((1000-128)/1100, (800-128)/700)` with the bbox centred, readout `79%`.
`Home` gives `{0,0,1}`. A 260×130 drag on empty space persists `{260,130,1}`,
and a click on the readout puts it back to `{0,0,1}`. Dragging a card 100 screen
px at zoom `0.7927` moves it `126.15` board px — the divide-by-zoom is real.
Home, Fit, the readout and the `pagehide` flush are all bound after load.

## Holes found and folded (this commit)

**H1 — one camera write could break the whole UI, permanently.** Python's
`json.loads` accepts `NaN` / `Infinity` / `-Infinity`, and `float("1e999")` is
`inf`, so `POST {"camera": {"x": 1e999}}` stored `{"x": Infinity, …}` in the row.
`json.dumps` writes those back as bare tokens, which is *not* JSON: after one
such write, `GET /api/projects/:id`, `.../camera`, `.../board` **and
`/api/projects`** were all unparseable by `JSON.parse`. Because `api()` in
`app.js` swallows a parse failure into `{raw: text}` on a 200, the project rail
would simply render empty — every project, not just the poisoned one — with no
error anywhere, and it stayed that way across restarts because the bad value was
on disk. Verified before the fix: `strict-json=False` on all four reads, row
holding `{"x": Infinity, …}`. `set_camera` now falls back to the default for any
non-finite result, so garbage in one axis costs you that axis and nothing else.

**H2 — a pan was lost if you switched projects within 180 ms of making it.**
`flushCamera` read `state.projectId` and `state.camera` when the timer *fired*,
not when the write was scheduled. Measured before the fix: pan project A to
`(310,170)`, click project B inside the debounce window — A stayed at its old
`(10,20)` and the single write that went out carried B's own camera to B. The
pan was gone with no error. Under a slower board load the same race lands A's
camera *on* B, i.e. corruption rather than loss. `persistCamera` now captures
`{projectId, camera}` at schedule time, `flushCamera` sends that captured pair,
the project-switch handler flushes first, and `pagehide` flushes the last write
instead of dropping it. Same scenario now: A holds `(310,170)`, B untouched, and
no write is addressed to B.

## Remaining holes

**R1 — zoom is anchored at the board origin, not the pointer.** The wheel
handler scales around `(0,0)` and leaves `x` / `y` alone, so zooming in walks
your content toward the bottom-right and you have to pan back or press Fit.
This is the biggest leftover for a canvas round and the one users notice first.
Anchoring needs the pointer position relative to `#boardWrap`:
`x' = px - (px - x) * z'/z`.

**R2 — a trackpad cannot pan, and pinch is not a gesture.** Every `wheel` event
zooms; two-finger scroll is a `wheel` event, so the ordinary pan gesture zooms
instead. macOS pinch arrives as ctrl+`wheel` and gets the same fixed step. The
handler also ignores `deltaY` magnitude and `deltaMode`, so one flick and one
careful tick move the same 8%.

**R3 — `x` / `y` are unbounded.** Only zoom is clamped. A fast pan can park the
content arbitrarily far off-screen; Home and Fit are the only way back. Pinned
by `test_pan_offsets_are_unbounded` (asserts current behaviour: `1e9` persists).

**R4 — `GET /api/projects/:id/board` does not 404.** An unknown id answers
`200 {"nodes": [], "camera": {0,0,1}}` while `.../camera` on the same id is a
404. Pinned by `test_board_of_a_missing_project_is_200_with_a_home_camera`.

**R5 — `POST .../camera` on an unknown id still runs `UPDATE` + `COMMIT`** before
discovering the project is missing and answering 404. No row changes, but it is
a pointless write under the app lock on every stray request.

**R6 — `_json` still serialises with `allow_nan` on.** The camera path is now
guarded at the store, but the guard is local. Any future float that reaches a
response non-finite reintroduces H1 on a different route.

**R7 — no keyboard path to Home / Fit.** Upload has `U`; the camera has nothing.
Click-to-reset on the readout is discoverable only through a `title` tooltip.

**R8 — Fit ignores the toolbar and the dock.** The padding is a flat 64 px, so
`.board-tools` still overlaps the top-left card after a Fit on a small window.

**R9 — two windows on one project fight.** The camera is per-project, not
per-view; the last debounced write wins and the other window is not told.

## Repro

```bash
cd <repo>
python3 -m unittest atelier.tests.evolve.test_opus_03            # 25 tests, OK (2 skip without node)
python3 -m unittest atelier.tests.evolve.test_opus_03 atelier.tests.test_helix atelier.tests.test_evolve
# gate: 59 tests, OK
python3 -m unittest discover -t . -s atelier/tests -p "test_*.py"
# 175 tests, OK (1 pre-existing expected failure)
```

Against `91cf452` (pre-fix) the new pins fail, which is what makes them pins:
`CameraStore.test_non_finite_never_reaches_the_row`,
`CameraRoute.test_non_finite_write_cannot_poison_later_reads`,
`CameraWiring.test_debounced_write_captures_its_project`,
`CameraWiring.test_pending_write_is_flushed_on_pagehide_and_project_switch`,
`BoardCameraJs.test_board_camera_behaviour`,
`BoardCameraJs.test_switching_projects_does_not_lose_or_cross_the_pending_write`.

The node tests need a `node` binary and skip cleanly without one; the
string-level wiring checks cover the same bindings on a machine that has none.
