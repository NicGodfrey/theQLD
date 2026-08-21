# Fable-05 — Round 9 (Undo) verification

**Verdict: PASS with documented holes.** The undo slice works end to end
(store → HTTP → web), but it is a single-shot destructive pop: no redo,
and undoing an image node orphans its artifact row and file.

## What was read

- `atelier/helix/store.py` — `undo_log` table (schema, `store.py:73-79`);
  `push_undo` (`store.py:318-325`) inserts `{id, project_id, action, payload,
  created_at}`; `add_node` (`store.py:252-278`) pushes an `add_node` entry with
  `{node_id, artifact_id}` after every insert, so conductor-woven variants and
  manual text layers are all undoable. `undo` (`store.py:327-339`) pops the
  newest entry per project (`ORDER BY created_at DESC, id DESC LIMIT 1`),
  deletes the node for `add_node` actions, deletes the log row, and returns
  `{"undone": True, action, payload}` or `{"undone": False, "reason": "empty"}`.
- `atelier/server.py:297-299` — `POST /api/projects/:id/undo` returns 200 with
  `app.memory.undo(...)` verbatim; empty body is fine.
- `atelier/web/index.html:52` — `#undoBtn` in board tools;
  `atelier/web/app.js:350-354` — click posts to the undo endpoint then
  `refreshBoard()`.

## Test evidence

`atelier/tests/evolve/test_fable_05.py` — 8 tests, all pass
(`python3 atelier/tests/evolve/test_fable_05.py`):

- `add_node` writes one `undo_log` row (`action=add_node`, correct `node_id`).
- Undo pops LIFO: with two nodes, only the second is removed.
- Empty log returns exactly `{"undone": False, "reason": "empty"}`.
- Undo is project-scoped; another project's log is untouched.
- HTTP: node create returns **201**, `POST .../undo` returns 200 with
  `undone=True` and the right `node_id`; second undo reports `empty`.
- Web wiring: `#undoBtn` exists and `app.js` posts `/undo` + refreshes.
- Hole checks (assert current behavior): no `Memory.redo`, and the artifact
  row survives node undo (`get_artifact` still non-None).

Release gate stays green: `python3 -m unittest atelier.tests.test_helix
atelier.tests.test_evolve` → 28 tests OK.

## Remaining holes

1. **No redo** — the log row is deleted on pop; an undone node is gone forever.
2. **Artifacts not deleted** — undoing an image node leaves the artifact row
   and the file under `.runtime/artifacts/`, still reachable via
   `/api/artifacts/:id` and included in export zips.
3. Only `add_node` is journaled: `update_node` (move/resize), `delete_node`,
   brand-kit and camera changes are not undoable.
4. Ordering ties on `created_at` fall back to `id DESC` (random uuid4 hex), so
   same-timestamp pops are LIFO-approximate, not guaranteed.
5. Server does not 404 on unknown project ids for undo; it returns
   `{"undone": False, "reason": "empty"}` (empty log and missing project are
   indistinguishable to the client).

## 8-line summary

1. Round 9 undo verified PASS across store, HTTP, and web layers.
2. `add_node` journals `{node_id, artifact_id}` into `undo_log` via `push_undo`.
3. `undo()` pops the newest per-project entry, deletes the node, returns payload.
4. `POST /api/projects/:id/undo` (200) and the `#undoBtn` → `refreshBoard()` wiring both work.
5. Empty-log undo cleanly returns `{"undone": false, "reason": "empty"}`.
6. Hole: no redo — popped entries are destroyed, not archived.
7. Hole: artifacts (rows + files) survive node undo and become orphans.
8. New `atelier/tests/evolve/test_fable_05.py`: 8/8 pass; release gate 28/28 stays green.
