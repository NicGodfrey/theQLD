# Fable-02 — Round 3 verification: progress events + `?stream=1` SSE

Scope: `atelier/helix/conductor.py` (`Conductor.run`, `on_event`, `events`),
`atelier/server.py` (`_sse_result`, `POST /api/threads/:id/run?stream=1`).
No live code was edited. New test: `atelier/tests/evolve/test_fable_02.py` (8 tests, all pass).

## What Round 3 claims vs. what the code does

`ROUNDS.md` R3: "`run.events` phases; `?stream=1` SSE" — **confirmed, with one caveat (post-hoc flush)**.

### Conductor event stream — confirmed

`Conductor.run` builds a local `events` list and an `emit()` closure that appends
each event and forwards it to the optional `on_event` callable
(conductor.py lines 121–128). Emission order on a fast demo run:

1. `phase: brief` (line 130)
2. `quote` — `emit("quote", quote=q)` (line 141), carries `estimated_usd` / `priced`;
   a `BudgetExceeded` raise follows immediately if the quote would exceed budget
3. `phase: score` (line 154), with `planner_fallback` emitted on planner failure (line 176)
4. `phase: route` with the resolved route payload (line 188)
5. `phase: weave` (line 215), then per-item `pin` events carrying
   `node_id` (+ `artifact_id`, `provider` for images) and `error` events on spoke failure
6. `phase: critique` — thinking mode only (line 306)
7. `phase: pin` (line 331)
8. `phase: done` (line 341), then `events` is returned inside the result dict (line 348)

So the required phases brief / score / route / weave / pin / done are all present and
ordered; `critique` is conditional on `mode="thinking"`. The `quote` event is present and
lands between `brief` and `score`. `on_event` receives the identical sequence
(verified by list equality in the test).

### Server SSE — confirmed, but replay-only

`POST /api/threads/:id/run` parses `stream` as truthy for `1|true|yes`
(server.py line 357), runs the conductor **synchronously with no `on_event`
argument** (lines 359–368), and only then calls `_sse_result` (lines 378–380).
`_sse_result` (lines 129–139) writes `text/event-stream; charset=utf-8`,
`Cache-Control: no-store`, one `event: <kind>` / `data: <json>` frame per buffered
event, and a terminal `event: result` frame with the full result dict, with a single
`flush()` at the end.

**Caveat (as flagged in the brief): events currently flush after the sync run, not
mid-weave.** The transport is SSE-shaped but the timing is a replay: a client
watching the socket during a slow paid weave sees zero bytes until `done`. My test
`test_documented_gap_server_flushes_events_after_sync_run` pins this by spying on
`conductor.run` and asserting the handler passes no `on_event`.

## Test run

```
python3 -m unittest atelier.tests.evolve.test_fable_02   # 8 tests, OK (2.1s)
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve   # 28 tests, OK — gate green
```

Coverage added beyond the existing `Round03Stream` test: full six-phase ordering
(brief first, pin→done last), quote-before-score, thinking-mode critique-before-pin,
pin events referencing real nodes, SSE frame parsing (frames == events + terminal
`result`), `stream=true|yes` aliases, `stream=0` JSON fallback, and the
post-hoc-flush gap.

## Remaining holes

1. **No live streaming** — the whole SSE body arrives after the run; progress UX value is nil
   for slow paid weaves. Fix is small (see diff below).
2. **Error paths bypass SSE** — `BudgetExceeded`/`ConductorError`/generic exceptions return
   plain JSON 402/422/500 even when `stream=1`; an SSE client gets a mid-protocol
   content-type switch instead of an `event: error` frame.
3. **POST-based SSE** — browser `EventSource` only speaks GET, so consuming this
   requires `fetch` + manual stream parsing; nothing in `web/app.js` does that
   (it hardcodes `?stream=0`, line 332), so the SSE path has no live consumer.
4. **No client-abort handling** — a disconnected client raises `BrokenPipeError`
   inside the handler once streaming becomes live (harmless today only because
   writes happen after the run).
5. **`critique` phase is undocumented** in the R3 phase list; harmless, but SSE
   consumers switching on `event:` names should know it exists.

## Unapplied diff (proposal only — not applied, live files untouched)

Stream events as they happen by wiring `on_event` into the handler; keep the JSON
error contract for non-stream calls and emit an `error` frame once headers are out:

```diff
--- a/atelier/server.py
+++ b/atelier/server.py
@@ POST /api/threads/:id/run
             stream = query.get("stream", ["0"])[0] in {"1", "true", "yes"}
+            push = None
+            if stream:
+                self.send_response(200)
+                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
+                self.send_header("Cache-Control", "no-store")
+                self.end_headers()
+
+                def push(ev: dict) -> None:
+                    self.wfile.write(f"event: {ev.get('kind', 'message')}\n".encode())
+                    self.wfile.write(f"data: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n".encode())
+                    self.wfile.flush()
             try:
                 result = app.conductor.run(
                     project_id=thread["project_id"],
@@
                     parent_artifact_id=body.get("parent_artifact_id") or body.get("spot_artifact_id"),
+                    on_event=push,
                 )
             except BudgetExceeded as exc:
+                if stream:
+                    push({"kind": "error", "code": "budget_exceeded", "message": str(exc)})
+                    return
                 _json(self, 402, {"error": str(exc), "code": "budget_exceeded", "ok": False})
                 return
             except ConductorError as exc:
+                if stream:
+                    push({"kind": "error", "code": exc.code, "message": str(exc)})
+                    return
                 _json(self, 422, {"error": str(exc), "code": exc.code, "ok": False})
                 return
             except Exception as exc:
+                if stream:
+                    push({"kind": "error", "code": "internal", "message": str(exc)})
+                    return
                 _json(self, 500, {"error": str(exc), "ok": False})
                 return
             if stream:
-                _sse_result(self, result)
+                self.wfile.write(b"event: result\n")
+                self.wfile.write(f"data: {json.dumps(result, ensure_ascii=False, default=str)}\n\n".encode())
+                self.wfile.flush()
                 return
```

(Follow-ups for the same slice: wrap `push` writes in `try/except BrokenPipeError`
so an aborted client cancels quietly, and have `web/app.js` opt into `?stream=1`
via `fetch` + ReadableStream to surface phase progress in the dock.)

## 8-line summary

1. R3 phases confirmed in `Conductor.run`: brief → quote → score → route → weave (+pin/error per item) → [critique] → pin → done.
2. `quote` event confirmed at conductor.py line 141 (`emit("quote", quote=q)`), before score, carrying `estimated_usd`.
3. `on_event` receives the exact same ordered sequence that `result["events"]` returns.
4. `?stream=1` (also `true`/`yes`) returns `text/event-stream`: one frame per event plus terminal `event: result`.
5. Caveat pinned by test: the handler never passes `on_event`, so SSE frames flush only after the sync run — no mid-weave progress.
6. Other holes: stream errors fall back to plain JSON (no `error` frame), POST-SSE is EventSource-incompatible, and `web/app.js` hardcodes `stream=0` so nothing consumes the stream.
7. New tests: `atelier/tests/evolve/test_fable_02.py` — 8/8 pass; release gate (`test_helix` + `test_evolve`, 28 tests) stays green.
8. Unapplied diff above wires `on_event` into the handler for true incremental SSE with `event: error` frames; live files untouched.
