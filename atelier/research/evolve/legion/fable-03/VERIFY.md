# Fable-03 · Round 5 verification — reference upload

**Verdict: PASS** (with two documented holes left for the conductor, pinned by tests;
three upload-validation holes found live and fixed in this pass).

Verified against `cursor/atelier-byok-studio-d639` at the R5 head
(`e0f9300 Round 5: wire reference upload and attach it to the next weave.`),
by reading the live tree and running real HTTP against `ThreadingHTTPServer`
on an ephemeral 127.0.0.1 port, demo provider only. No paid calls, no keys.

## Path traced

**Route** — `atelier/server.py`, `_do_POST` branch
`parts[:2] == ["api","projects"] and parts[3] == "upload"`:
404 on missing project → base64 decode → 5 MB cap (413) → `Memory.add_artifact(kind="upload",
provider="local", model="upload")` → `loom.write_bytes` (path is `<artifact_id><ext>` under the
runtime artifacts dir, so the client filename never touches the filesystem) → `Memory.add_node`
(`type="image"` for `image/*`, else `note`) → 201 `{artifact, node}`.

**JS bindings** — `atelier/web/app.js`:

- `#uploadBtn.onclick` → `document.getElementById("filePick").click()` (line ~393)
- `#filePick` `change` → `uploadFile(file)`, input value reset so the same file can re-upload
- board drop: `wrap.addEventListener("drop", …)` in `enableBoardCamera` → `uploadFile(file)`
- keyboard `U`: `keydown` handler skips `input, textarea, select, [contenteditable]`, then clicks `#filePick`
- `uploadFile` posts `{filename, mime, data}` (base64 via `bytesToBase64`), then sets
  `state.lastUploadId = state.lastArtifactId = result.artifact.id`

**parent_artifact_id** — `runBody()` sends
`parent_artifact_id: spot ? state.lastArtifactId : (state.lastUploadId || undefined)` where
`spot = state.lastArtifactId && /spot|局部|edit this/i.test(prompt)`. Both the project-list click
handler and `#newProject` set `state.lastUploadId = null` (claim 5, pinned by
`test_project_switch_and_create_clear_last_upload`). Server side, `/api/threads/:id/run` passes
`body.parent_artifact_id` into `Conductor.run`, which resolves the parent, sets
`plan.spot_edit.parent_id`, prefixes the weave prompt with the spot-edit direction, and stamps
`parent_id` on every new artifact row.

## Live HTTP evidence (before fixes → after fixes)

| Probe | Before | After |
|---|---|---|
| `POST /api/projects/:id/upload` valid svg | 201, `artifact.kind="upload"`, `node.type="image"`, `node.artifact_id == artifact.id` | same |
| 5,000,001-byte payload | 413 `upload too large` | same |
| `data: "!!!!"` (garbage base64) | **201, 0-byte artifact + board node** | 400 `invalid base64` |
| `data: ""` / whitespace / null | **201, 0-byte artifact** | 400 `empty upload` |
| `mime: text/html` then `GET /api/artifacts/:id` | **served `Content-Type: text/html`** (uploaded HTML would execute on the app origin) | stored/served `application/octet-stream`, node type `note` |
| ~8.7 MB JSON body | fully buffered + decoded before 413 | 413 from `MAX_JSON_BODY` guard, body drained, no decode |
| `POST /api/threads/:id/run` with `parent_artifact_id=<upload id>` | 200, `artifacts[0].parent_id == <upload id>`, `plan.spot_edit.parent_id == <upload id>` | same |
| same with bogus parent id | 200, **`artifacts[0].parent_id="no-such-artifact"`**, no `spot_edit` | unchanged, pinned (see holes) |
| `GET /api/projects/:id/board` after upload | upload node present with `artifact_id` | same |

Board node placement uses the same 3-column grid offsets as the conductor
(`72 + (n%3)*360, 72 + (n//3)*280`) — uploads and weaves don't stack on top of each other.

## Fixes shipped in this pass (all inside the upload path)

`atelier/server.py`:

1. Reject empty/non-string `data` with 400 before decoding.
2. `base64.b64decode(..., validate=True)` (whitespace stripped first so wrapped base64 still
   works) — garbage no longer silently strips to an empty blob; empty decodes are 400.
3. Pre-decode length gate on the base64 string (6.8 M chars ≈ 5 MB decoded) plus a shared
   `MAX_JSON_BODY` (8 MB) guard in `_read_json` that drains and 413s oversized bodies before
   any json/base64 work. The old cap only fired *after* buffering and decoding the whole body.
4. Mime safelist: `image/*`, `application/pdf`, `text/plain`, `application/json` are kept;
   everything else is coerced to `application/octet-stream`. This closes the stored-HTML hole:
   `/api/artifacts/:id` echoes the artifact mime, so a `text/html` upload used to come back
   executable on the app origin (same origin as `/api/keys`). SVG stays allowed because
   `_send_file` already serves it with a sandboxing CSP.

Tests tightened in `atelier/tests/evolve/test_fable_03.py` (12 tests): the four fixes above,
plus wiring pins for claim 4 (spot regex prefers `lastArtifactId`) and claim 5 (project
switch/create clears `lastUploadId`), plus a pin of the dangling-parent current behavior.

## Folded after this note (conductor close)

Dangling `parent_id` is now NULL when the parent does not resolve.
`state.lastUploadId` is cleared on a successful Weave so a reference is one-shot.

## Remaining holes

1. **No dedicated reference picker.** The next weave always uses the *latest* upload.
2. Uploads are artifacts with `thread_id=NULL`; the chat transcript does not record the drop.

<!-- 说明：以上四条是留给指挥者的收尾项，前两条已经用测试钉住当前行为，
     修复后请同步翻转对应断言。 -->

## Gate

```
python3 -m unittest atelier.tests.evolve.test_fable_03 atelier.tests.test_helix atelier.tests.test_evolve
Ran 46 tests … OK
```

Verifier: Fable-03 (`claude-fable-5-thinking-high`), single blocking agent for R5.
