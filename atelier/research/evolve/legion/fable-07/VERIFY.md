# Fable-07 · R13 designer export — verified

Verifier: one live `claude-fable-5-thinking-high` agent, branch
`cursor/atelier-byok-studio-d639`, HEAD at `88e094d` (Round 13).
Method: read the live tree, drive a real `ThreadingHTTPServer` on a throwaway
`ATELIER_RUNTIME`, exercise every export route with `urllib` — demo lane only,
no network, no key read, no paid call. Zip members, SVG structure, PNG IHDR
and PDF trailer were checked byte-for-byte, not by header alone.

**Verdict: PASS with fixes.** All five claims held as shipped. The formats
themselves are honest — the zip still archives, text stays `<text>`, JPEG is
refused with a code, the rights line is everywhere it should be. What did not
hold was the arithmetic around the sheet: one node dragged far enough off the
board made the *default* zip export try to allocate a petabyte, and the
artifact SVG scaler edited the wrong element on uploads.

## Claim by claim

| # | Claim | Verdict |
|---|-------|---------|
| 1 | Default `GET /export` is a zip (`PK`, nosniff, attachment) with project/board/threads/artifacts JSON, artifact bytes, plus `board.svg`, `sheet.png`, `sheet.pdf`, `RIGHTS.txt` | PASS |
| 2 | `board.svg` keeps text layers as `<text>` (Headline @ font-size 36); SVG artifacts inline as vector, PNG embeds as data URI | PASS |
| 3 | `?fmt=svg\|png\|pdf&scale=` returns the right mime; PNG/PDF magic; scale snaps 1/2/4; SVG download carries the artifact-view CSP sandbox | PASS, with the sheet buffer capped |
| 4 | `/api/artifacts/:id/export?fmt=native\|svg\|png\|pdf`; JPEG → 415 `unsupported_fmt`; missing → 404 | PASS, with `scale_svg` fixed for uploads |
| 5 | `#exportDialog` + `#exportRights` ("Atelier grants none") + scale select; per-card Export → `fmt=png`; `OUTPUT_RIGHTS.md` and `RIGHTS.txt` agree | PASS |

## Path traced

`#exportZip` click → `showModal()` on `#exportDialog` (or, with no
`showModal`, straight `window.location = /api/projects/:id/export`, which is
the default zip — the fallback ends on the same route this note verifies) →
`#exportGo` reads the checked `exportFmt` radio and `#exportScale` →
`GET /api/projects/:id/export?fmt=&scale=` → `server._do_GET` →
`export_scale` snaps the query → `export_project_bytes` dispatches:

- `zip|archive` → `exportzip.export_project_zip` → `project.json`,
  `board.json` (nodes + camera), `board.svg`, `sheet.png`, `sheet.pdf`,
  `RIGHTS.txt` (the module's `RIGHTS_TEXT` verbatim), `threads.json` with
  `messages` per thread, `artifacts/<id>.<ext>` bytes, `artifacts.json`
  manifest (paths swapped for filenames).
- `svg` → `board_svg`: for each node, an image node reads its artifact from
  disk — SVG bytes are inlined via `_place_svg` (root re-positioned, XML
  prolog stripped), rasters become `<image href="data:...;base64,">` — and
  everything else becomes `<text>` with `font_size` / `font_family` /
  `letter_spacing` off `node.meta`, `html.escape`d.
- `png|pdf` → `render_sheet_rgb` paints a contact sheet into a raw RGB
  buffer with a 5×7 bitmap font, then `encode_png` (zlib IDAT) or
  `rgb_to_pdf` (one page, DeviceRGB XObject, Helvetica rights line).

`FormatError` (jpeg/jpg/unknown) → 415 with `code`; `ValueError` (missing
project) → 404. `_send_bytes` adds nosniff + attachment on every branch and
the `default-src 'none'; style-src 'unsafe-inline'; sandbox` CSP whenever the
mime is `image/svg` — the same header `_send_file` puts on the artifact view.

The per-card path is one link: `/api/artifacts/:id/export?fmt=png` →
`export_artifact_bytes` → native PNG bytes pass through; an SVG artifact
becomes a labeled card (below, honestly). `meta.font_size` is trustworthy at
render time because `store.add_node` / `update_node` run every meta through
`loom.text_meta` (R12 fix), so `float(size)` cannot see junk.

## HTTP evidence

Claim 1 — one project, one demo weave, one text node, one uploaded 2×2 PNG:

```
GET /api/projects/<id>/export
200  PK  Content-Type: application/zip  X-Content-Type-Options: nosniff
     Content-Disposition: attachment; filename="atelier-r13-verify.zip"
members: RIGHTS.txt artifacts.json artifacts/<png-id>.png artifacts/<svg-id>.svg
         board.json board.svg project.json sheet.pdf sheet.png threads.json
threads.json: messages roles [user, assistant]   RIGHTS.txt == RIGHTS_TEXT: True
```

Claim 2 — inside that zip's `board.svg`:

```
<text x="40.0" y="76.0" fill="#f4f1ea" font-size="36.0"
      font-family="Georgia, serif" letter-spacing="normal">Headline</text>
demo artifact: nested <svg ... x= y= width= height=>   (vector, not baked)
uploaded png:  <image ... href="data:image/png;base64,iVBOR..."/>
no <image> anywhere carries the text node's string
```

Claim 3:

```
GET ?fmt=svg&scale=2   200 image/svg+xml
     CSP: default-src 'none'; style-src 'unsafe-inline'; sandbox  == GET /api/artifacts/<id> CSP
     width="2304.0" viewBox="0.0 0.0 1152.0 352.0"   (scale bumps size, not the coordinate system)
GET ?fmt=png scale 1/3/9 → PNG IHDR widths 640 / 1280 / 2560   (3 snaps to 2, 9 to 4)
GET ?fmt=pdf           200 application/pdf   b'%PDF-' ... b'%%EOF'
zip?scale=4: board.svg width 4608, sheet.png width 2560   (scale reaches inside the archive)
```

Claim 4:

```
svg artifact  fmt=native|svg → image/svg+xml (+CSP)   fmt=png → \x89PNG   fmt=pdf → %PDF..%%EOF
png artifact  fmt=native|png → the artifact's own bytes   fmt=svg → data-URI wrap, real 2×2 viewBox
fmt=jpeg|jpg  415 {"error":"jpeg export is not in the stdlib slice","code":"unsupported_fmt"}
fmt=webp      415 {"code":"unsupported_fmt"}
/api/artifacts/deadbeef/export → 404      artifact row whose file is gone → 404, not 500
/api/projects/deadbeef/export?fmt=zip|svg|png|pdf → 404
```

Claim 5 — live `web/index.html` has `#exportDialog`, four `exportFmt` radios,
`#exportScale` (1×/2×/4×) and `#exportRights` containing "Atelier grants
none"; `app.js` renders `/api/artifacts/${node.artifact_id}/export?fmt=png`
on every image card and falls back to the plain `/export` zip when
`showModal` is missing. `OUTPUT_RIGHTS.md` and `RIGHTS.txt` both say "does
not grant commercial rights" over the same four provider lines.

## Holes found and closed

1. **One far-flung node OOM'd every sheet render — including the default
   zip.** `x`/`y` are only checked for *finiteness* on write (R12's guard was
   about JSON, not magnitude), and `render_sheet_rgb` sized its buffer as
   `inner_w * bh / bw` with no cap. `POST /nodes {"y": 1e12}` then
   `GET /export` asked for a 3.6 PB bytearray — captured as `MemoryError`
   under a rlimit; on a lazier allocator it is minutes of `_fill` loops
   holding `app.lock`, which stalls the whole single-process studio. At
   `y=1e308` the float overflows to `inf` and `int()` raises instead. The
   sheet aspect is now capped at 4:1 of the inner width, so the far node
   flattens into the top band rather than sizing the buffer. Nothing catches
   `MemoryError` in `server.py`; the cap at the source is the fix.
2. **`scale_svg` scaled the first two width/height attributes *anywhere*, not
   the root's.** Fine for the demo SVG (root carries both), wrong for
   uploads: `<svg viewBox="0 0 100 50"><rect width="100" height="50"/>`
   at `?fmt=svg&scale=2` came back with the *rect* doubled inside an
   unchanged viewport — a corrupt drawing. It now edits only the root tag,
   derives width/height from the viewBox when the root has none, and leaves
   the bytes alone when there is neither.
3. **`wrap_raster_svg` stretched every raster onto a 1024×1024 square.** A
   non-square uploaded PNG exported as `fmt=svg` was silently distorted.
   Dimensions need no decoder — `png_dimensions` reads the IHDR — so the wrap
   now carries the artifact's true viewBox (`0 0 2 2` for the test swatch).

### Checked and *not* a hole

- **Text cannot inject into `board.svg`.** Node text is `html.escape`d
  (`<script>` arrives as `&lt;script&gt;`), and a hostile
  `font_family="serif\" onload=..."` never reaches the SVG because
  `loom.text_meta` drops it on write; the attribute is escaped at render
  anyway.
- **`fmt=archive` alias, empty projects, and ghost artifacts behave.** An
  empty board exports a 1024×1024 placeholder SVG and a full zip; an artifact
  row whose bytes are gone is 404, not a traceback.
- **Errors are ordered right.** `FormatError` subclasses `ValueError`, and
  the server catches it first, so jpeg is 415 and a missing project 404 on
  the same route.

## Evidence that the tests bite

Against the shipped `88e094d` `exportfmt.py` (with only a `png_dimensions`
shim so the module imports), the four new hole tests fail exactly as claimed:
`test_far_flung_node_does_not_size_the_buffer` dies in `MemoryError` under a
2 GB rlimit, `test_scale_svg_only_touches_the_root_tag` sees the nested rect
doubled, and both raster-dimension tests get the 1024×1024 stretch. All 22
pass on the fixed module.

## Tests

`atelier/tests/evolve/test_fable_07.py` — was 15 tests; now 22. New:
`ClosedHoles` pins the three fixes; the HTTP suite now checks zip membership
+ threads-with-messages + `RIGHTS.txt == RIGHTS_TEXT` + `>Quiet type</text>`
over the wire, scale snap via PNG IHDR widths (1/3/9 → 640/1280/2560), CSP
equality between `fmt=svg` and the artifact view, `%%EOF` on both PDF routes,
`code=unsupported_fmt` on the artifact jpeg, 404 across all four fmts of a
missing project and for a bytes-gone artifact row, the uploaded-PNG data-URI
ride through `board.svg`, the `<dialog>`-fallback string, and the CJK slug
falling back to the id (known hole, pinned as current behaviour).
`Round13Export` in `atelier/tests/test_evolve.py` passes untouched.

```
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve \
    atelier.tests.evolve.test_fable_07
Ran 56 tests — OK
```

Full tree (`unittest discover -s atelier/tests`): 264 tests, OK
(1 expected failure, pre-existing).

## Remaining holes (none blocking)

- `sheet.png` / `sheet.pdf` are a painted contact sheet, and SVG→PNG per
  artifact is a labeled card — neither is a browser raster of the live board.
  The module docstring says so; kept honest, not fixed (a rasterizer is not a
  stdlib slice).
- Native PNG artifacts ignore `scale` on `fmt=png` (verified: scale=4 returns
  the native bytes unchanged) — there is no PNG decoder to resample with.
- CJK captions on the bitmap sheet degrade to `·` / fallback glyphs
  (5×7 ASCII font); `board.svg` is the UTF-8 deliverable and carries them
  intact. CJK project names also slug to the id in filenames (R4 hole,
  now pinned).
- An uploaded SVG's markup is inlined into `board.svg` verbatim (positioned,
  prolog stripped, but not sanitised). Served over `fmt=svg` it is defused by
  the CSP sandbox; opened from the zip it is whatever the artifact already
  was. Same trust boundary as the artifact file itself.
- A board of many large data-URI rasters makes `board.svg` (and the zip)
  big — base64 is ~4/3 of the bytes already on disk, bounded by the 5 MB
  upload cap per artifact. Not obviously broken; no size cap added.
