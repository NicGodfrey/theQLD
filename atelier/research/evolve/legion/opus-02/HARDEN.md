# Opus-02 — Round 4 (artifact download) verification

**Verdict: PASS.** `GET /api/artifacts/:id` serves inline, so `<img src="/api/artifacts/:id">`
renders on the board; `?download=1` is the only thing that adds
`Content-Disposition: attachment`, and the filename is the brief slug from
`atelier.helix.loom.download_filename`, not the hex artifact id. `_send_file` sends
`X-Content-Type-Options: nosniff` on every response, and the artifact path is confined by
`safe_under(app.artifacts, Path(art["path"]))`. Every claim below was checked over real HTTP
against a live `ThreadingHTTPServer`, not by reading the source. This supersedes the earlier
conductor-fill note on this page, whose "remaining" list (hex filename, missing `nosniff`) is
now stale — both were fixed.

Scope: read-only over `atelier/server.py`, `atelier/helix/loom.py`, `atelier/helix/paths.py`,
`atelier/web/app.js`. No live file was edited. Tests live in `atelier/tests/evolve/test_opus_02.py`.

## Path traced

| Step | Where | Behaviour |
|---|---|---|
| Board image | `web/app.js` | `img src = /api/artifacts/${node.artifact_id}` — no query, so inline |
| Download link | `web/app.js` | separate `<a href=".../${id}?download=1">Download</a>` |
| Route | `server.py`, `GET /api/artifacts/:id` | 404 JSON `missing artifact` when the row is absent |
| Intent | `server.py` | `force = query["download"][0] in {"1","true","yes"}` |
| Name | `loom.download_filename` | prompt → `[a-z0-9-]{,32}` slug + `ext_for_mime(mime)`; hex id only as fallback |
| Confinement | `paths.safe_under` | `resolve()` + `relative_to(root)` + `is_file()`; else 404 `not found` |
| Send | `server.py`, `_send_file` | `Content-Type`, `Content-Length`, `nosniff`; `Content-Disposition` only when `force` |

(Symbols, not line numbers: the live tree is moving under other legion agents.)

## Live evidence

Fresh runtime, demo lane, brief "Queensland Legal Directory poster". Plain `GET` returns
`200`, `Content-Type: image/svg+xml`, `X-Content-Type-Options: nosniff`, a `Content-Length`
matching the body, an SVG payload, and **no** `Content-Disposition` — an `<img>` renders it
instead of triggering a save dialog. The same id with `?download=1` returns exactly
`attachment; filename="queensland-legal-directory-poste.svg"`: the brief slug, the mime
extension, the hex id absent, and exactly two quote characters in the header. `?download=true`
and `?download=yes` behave the same; `?download=0`, `?download=false` and a bare `?download=`
stay inline.

Containment holds against three shapes of bad row, all 404 with no bytes leaked: an artifact
whose `path` is `/etc/passwd`, one whose `path` contains `../..` dot segments, and a symlink
planted *inside* the artifacts directory pointing at a file outside it (`resolve()` follows the
link before the `relative_to` check, so the escape is caught). Filenames cannot inject headers:
a prompt of `poster"; filename="pwned.html\r\nSet-Cookie: a=b` slugifies to `[a-z0-9-]` only,
which is why the unescaped `filename="{...}"` interpolation in `_send_file` is safe today —
safe by the slug's construction, not by any escaping at the header.

## Folded after this note (conductor, sequential close)

H1 CSP + sandbox on SVG GET. H3 trailing hyphen + `ref.svg` stem. H4 `on`/`True`/`YES`
(case-insensitive). H6 `_send_bytes` nosniff. H7 `_send_file(..., mime=row.mime)`.

## Remaining holes

**H2 — Non-ASCII briefs still get the hex id.** `download_filename` strips everything outside
`[a-zA-Z0-9]`, so a Chinese-only brief ("四宫格 海报") slugifies to the empty string and falls
back to `id[:12]`. RFC 5987 `filename*=UTF-8''…` is the leftover.

**H3 leftover — same-brief collision.** Two artifacts from the same brief still produce
byte-identical filenames.

**H5 — No `HEAD`, no conditional or range requests, whole file buffered.** `HEAD` is still 501.
No `ETag` / `Last-Modified` / `Cache-Control` / `Accept-Ranges`.

## Repro

```bash
cd <repo> && python3 -m unittest atelier.tests.evolve.test_opus_02   # 26 tests, OK
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve atelier.tests.test_evolve.Round04DownloadName
# gate: 35 tests, OK
```

Full discovery after adding this agent's tests: 137 tests, OK (1 pre-existing expected failure).
