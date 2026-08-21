# Opus-06 · R12 text layer — verified

Verifier: one live `claude-opus-5-thinking-high-fast` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `b6829c9` (Round 12).
Method: read the live tree, drive a real `ThreadingHTTPServer` on a throwaway
`ATELIER_RUNTIME`, and run the live `atelier/web/app.js` under node against
that same server through a DOM shim. Demo lane only — no network, no key read,
no paid call.

**Verdict: PASS with fixes.** All five claims held as shipped. The round's
promise — type stays type, size lives on the node — is true end to end. What
did not hold was everything *around* the write: the node route was the one
board write with no project check, no numeric coercion and no meta
normalisation, and two bodies could brick a board permanently.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | `type=text` creates a node with `type="text"` and no `artifact_id` | PASS |
| 2 | `#textLayer` parses `Headline · 32`, board renders it as CSS on `.text-body` | PASS, with a clamp moved server-side and two UI holes closed |
| 3 | `data` is an alias for `text` on `add_node` and `update_node` | PASS |
| 4 | A refresh / `GET .../board` rehydrates type, text and `font_size` | PASS |
| 5 | Weave `kind=text` → type=text node, `kind=note` → note, no artifact | PASS |

## Path traced

`#textLayer` click → `window.prompt` → split on `·` → clamp 12–96 →
`POST /api/projects/:id/nodes {type:"text", text, meta:{layer, font_size}}` →
`server._do_POST` → `Memory.add_node` (no `artifact_id`, no `write_bytes`, no
`artifacts` row) → `push_undo` → back on the page, `refreshBoard` →
`GET /api/projects/:id/board` → `Memory.list_nodes` → for a node with no
`artifact_id`, the else branch builds a `.text-body` div and writes
`style.fontSize` / `fontFamily` / `letterSpacing`. The card also gets
`.note .text-layer`, which is CSS, not pixels.

The conductor's typographic lane is the same store call: `Conductor.run`
sees `kind in {"note","text"}`, calls `add_node(type="text" if kind=="text"
else "note", meta={"layer":"text"} if text else {})` and `continue`s *before*
`_image_model` / `spoke.image` / `write_bytes` / `usage.record`.

## HTTP evidence

Claim 1 — text never reaches the raster:

```
POST /api/projects/<id>/nodes  {"type":"text","text":"Headline","x":120,"y":120,
                                "meta":{"layer":"text","font_size":32}}
201 {"type":"text", "artifact_id":null, "text":"Headline",
     "meta":{"layer":"text","font_size":32}, ...}
runtime/artifacts/ -> []        SELECT COUNT(*) FROM artifacts -> 0
```

Claim 4 — the same node after `GET /board`, and again after `reset_app()`
throws away every in-process object:

```
GET /api/projects/<id>/board
200 {"nodes":[{"type":"text","artifact_id":null,"text":"Quiet, precise",
      "meta":{"layer":"text","font_size":44,"font_family":"Georgia, serif",
              "letter_spacing":"0.08em"}}], "camera":{...}}
```

Claim 2 — real `app.js` under node, reading the element it wrote to. Four
clicks with `prompt()` answering `Headline · 32`, `Tiny · 5`, `Huge · 500`,
`Junk · not-a-number`:

```
POST bodies    font_size: [32, 12, 96, 32]
rendered       .text-body style.fontSize: ["32px","12px","96px","32px"]
card class     "node note text-layer"      img children: 0
board <img>    0        /api/artifacts/ fetches: 0
```

Claim 5 — a plan of `[{kind:"text"},{kind:"note"}]` through the real
`Conductor` with a stub planner:

```
nodes      [("text","HELIX",None,{"layer":"text"}),
            ("note","remember the grid",None,{})]
artifacts  []      files on disk: []      usage unit_kinds: no "images"
```

Adding `{kind:"image"}` to the same plan does mint one `.svg` and one artifact
row, so the text branch is skipping the raster rather than the raster being
broken.

## Holes found and closed

1. **A junk `meta` bricked the board, permanently.** `update_node` stored a
   `meta` that was already a string verbatim, so
   `POST /api/nodes/<id> {"meta":"not json"}` — one request, no auth beyond
   being on localhost — made `list_nodes` raise inside `json.loads`. After
   that `GET /api/projects/:id/board` was a 500 for *every* node in the
   project, and the UI has no other way in: the board never loads again.
   `meta` is now normalised on write and parsed defensively on read, so a row
   poisoned before the fix heals on the next read.
2. **`Infinity` in a coordinate did the same thing to JSON.** `{"y":Infinity}`
   survived `json.loads` and the insert, then `json.dumps` wrote a bare
   `Infinity` token into `/board` — captured verbatim from the shipped tree:

   ```
   200 {"nodes": [{... "x": 80.0, "y": Infinity, ...}], "camera": {...}}
   ```

   `JSON.parse` rejects that, so `refreshBoard` throws and the board is blank
   until someone edits sqlite. `set_camera` had guarded exactly this since R6
   and even carries the comment; the node route never got the same guard.
3. **A null or NaN coordinate dropped the connection.** Both land as SQL NULL
   against a `NOT NULL` column, so `{"y":null}` raised `IntegrityError` out of
   `_do_POST` with no response written at all — the client saw
   `RemoteDisconnected`, not a 4xx. Coordinates now coerce to finite floats
   with the column defaults; a junk coordinate in an *update* is a no-op
   rather than a jump back to (80,80).
4. **The node route was the only board write with no project check.**
   `POST /api/projects/deadbeef/nodes` answered 201 and wrote a card, plus an
   undo row, onto a board that `GET /board` 404s on forever. Brand and camera
   had been 404 since R10. Now this is too.
5. **Only the browser clamped `font_size`.** `meta.font_size` of 99999 stored
   as 99999; `"40px; background: red"` stored as-is. The board re-clamps on
   render so nothing was visibly broken today, but the *stored* number is what
   R13's designer PNG/PDF will read, and the clamp being client-only means
   every future client re-implements it. `loom.text_meta` now clamps 12–96
   server-side, drops a non-numeric size, and refuses a `font_family` or
   `letter_spacing` that CSS would not take — same shape as R10's
   `brand_colors` / `brand_name`. Keys the board does not read pass through.
6. **`POST /api/nodes/<missing>` raised `TypeError`** out of `dict(None)` and
   dropped the connection. Now 404 `{"error":"missing node"}`.
7. **Cancel minted a card.** `prompt(...) || "Headline · 32"` treats `null`
   the same as an empty answer, so dismissing the text-layer dialog placed a
   default "Headline" on the board. Cancel is now a no-op, on create and on
   edit.
8. **`font_family` and `letter_spacing` were unreachable from the UI.** The
   board has rendered both since R12 shipped, but `#textLayer` only ever wrote
   `font_size`, so the only way to set them was curl. The size prompt now
   takes optional tails — `Headline · 32 · Georgia, serif · 0.08em` — and
   `Headline · 32` behaves exactly as before.
9. **A text layer was write-once.** There was no click-to-edit at all on the
   live board (not `window.prompt`, nothing) — a placed card could only be
   dragged or undone. Double-click now reopens the same dialog prefilled and
   writes through `POST /api/nodes/:id`.

### Checked and *not* a hole

- **`font_family` / `letter_spacing` as raw CSS strings cannot inject.**
  `refreshBoard` assigns them through the CSSOM property setters
  (`style.fontFamily = …`), which parse a single property value; a `;` makes
  the value invalid and the browser drops the whole declaration rather than
  starting a new one. Text goes in as `textContent`, never `innerHTML`. They
  are validated now anyway, because R13 will interpolate them into an SVG or
  PDF where the same string is no longer inert.
- **An arbitrary `type` is inert.** `type` is a free string and
  `"<script>alert(1)</script>"` stores fine, but the board only ever compares
  it, and anything that is not an image-with-artifact renders through the text
  branch. Pinned as current behaviour.
- **`update_node`'s allow-list holds.** `type`, `artifact_id` and `project_id`
  are not patchable, so a text layer cannot be re-pointed at another project's
  artifact.

## Evidence that the tests bite

- Against the shipped `b6829c9` product files with the new suite:
  **22 of 34 fail** (9 failures, 13 errors). The 12 that pass are the five
  claims — `type=text` with no artifact, the `data` alias, the board
  round-trip, the conductor's text/note split, the CSS render — plus the two
  pins-current-behaviour tests.
- Reverting only `server.py`: `test_nodes_on_a_missing_project_are_404` and
  `test_patching_a_missing_node_is_404` fail.
- Reverting only `update_node`'s meta normalisation:
  `test_font_size_is_clamped_on_the_way_in` fails. The board no longer bricks
  because the read side heals it — that guard is pinned separately by
  `test_a_row_poisoned_before_the_fix_still_reads`.

## Tests

`atelier/tests/evolve/test_opus_06.py` — was 2 tests (one substring check over
`index.html` / `app.js` / `styles.css`, one HTTP POST); now 34 across six
classes. The substring class survives as a cheap gate for machines with no JS
runtime, but claim 2 is now checked by running the shipped `app.js`: three
node scenarios cover create, double-click edit, and a *fresh process* against
the same server, which is a real page refresh rather than a second in-page
render. `Round06to12Board.test_text_layer_not_raster` in
`atelier/tests/test_evolve.py` still passes untouched.

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_opus_06
Ran 68 tests — OK
```

Full tree (`unittest discover -s atelier/tests`): 239 tests, OK
(1 expected failure, pre-existing).

## Folded after this note (conductor close)

`w` / `h` clamp to 40–2400 (`1e308` is finite, so the Infinity guard was not
enough). A text card grows on insert so a 96px headline is not clipped by the
default 120px box. `POST /api/projects/:id/threads` on a missing project is
404 — same class as hole 4.

## Remaining holes

- Editing is still a `window.prompt` dialog, not a caret on the card. Nothing
  wraps, kerns or aligns interactively, and there is no font picker — the
  family is whatever string you type.
- The export zip carries text nodes in `board.json` only — no rendered
  PNG/PDF. That is R13, deliberately not started here.
