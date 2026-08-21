# Fable-04 · Round 7 (visible plan) — VERIFIED

Verdict: **PASS** (live tree at `934c7d4` + `787d050`; tests tightened by the
verifier, no product-code fixes needed).

## Path traced (live files)

1. **Plan stored on assistant messages.** `helix/conductor.py` builds the plan
   (fallback → demo-conductor parse → route/quote merge) and unconditionally
   persists it: `self.memory.add_message(thread_id, "assistant", summary,
   plan=plan)`. `helix/store.py` serialises it into the `plan_json` column and
   `list_messages` rehydrates `row["plan"]`, so `GET
   /api/threads/{id}/messages` returns the blob.
2. **Dock card on run and refresh.** `web/index.html` ships
   `<div id="planCard" class="plan-card hidden">`. `web/app.js`
   `renderPlan(plan)` fills it with `.plan-title` (intent), `.plan-meta`
   (mode · route provider/model) and an `ol.plan-steps` capped at
   `weave.slice(0, 4)`. It is called from both entry points: the run button
   (`renderPlan(result.plan)`) and `refreshMessages()` (`renderPlan(lastPlan)`
   after scanning `if (m.plan) lastPlan = m.plan`), so a page refresh
   rehydrates the card from the stored message.
3. **Clickable steps.** Each `li.plan-step` gets an `onclick` that
   `classList.toggle("done")` and drives the composer: un-skipping a step
   loads `w.prompt` into `#prompt`; skipping clears the composer only when it
   still holds that exact prompt. All text goes through `el(..., { text })`
   → `textContent`, so plan/critique content cannot inject HTML.
4. **Separate critic card.** Non-empty `plan.critique` appends a dedicated
   `.plan-critic` div to the card. `styles.css` styles `.plan-step`,
   `.plan-step.done` (line-through) and `.plan-critic` (top border). Fast mode
   leaves `critique` empty, so no phantom critic block renders.

## HTTP evidence (real `ThreadingHTTPServer`, demo provider, temp runtime)

- `POST /api/threads/{id}/run` (mode=thinking, "directory poster") → 200 with
  `plan.intent="directory poster"`, `plan.route={provider: demo, model:
  demo-conductor, capability: image}`, 1 weave step, and a non-empty
  `plan.critique` ("Type hierarchy is readable and the navy field is quiet…").
- `POST …/run` (mode=fast) → 200 with a plan whose `critique` is `""`.
- `GET /api/threads/{id}/messages` → both assistant messages carry their
  stored `plan`; the persisted thinking critique is byte-identical to the run
  response's critique (refresh shows the same critic card).

## Tests

`python3 -m unittest atelier.tests.evolve.test_fable_04 atelier.tests.test_helix
atelier.tests.test_evolve` → **all pass** (37 tests), including
`Round06to12Board.test_plan_visible_on_message`. Verifier tightened
`test_fable_04.py`: pinned the refresh render path
(`renderPlan(lastPlan)` / `renderPlan(result.plan)`), the 4-step cap, the
composer binding, critique persistence across the message round-trip, and a
new fast-mode test asserting the plan is stored without a forced critique.

## Remaining holes (fold before closing R7, none blocking)

- Step "done" state is client-side only; a refresh re-renders the card from
  the stored plan and drops any checked-off steps. Persisting per-step state
  would need a message-plan PATCH route.
- A step's first click marks it done (skip); loading the prompt into the
  composer happens on the un-skip click. Works as the commit describes, but a
  one-click "load" affordance may read better in usability passes.
- `renderPlan` shows only the latest assistant plan in the thread; older plans
  are reachable only through the raw messages list.
