# Opus-01 · Round 2 audit — quote-before-commit

Scope: `atelier/helix/quote.py`, `atelier/helix/usage.py` (`is_priced`), `POST /api/quote`
in `atelier/server.py`, and the Quote button in `atelier/web/app.js`.
Read-only audit. No live file was touched; the only files written are this report and
`atelier/tests/evolve/test_opus_01.py`.

## Verdict

| Claim | Verdict | Evidence |
|---|---|---|
| Unknown models quote `priced:false`, not fake-free | **PASS** | `is_priced` has no fallback branch; unknown OpenAI model quotes `priced=false`, `estimated_usd == conservative_usd == $0.05` at count 1 |
| demo / ollama quote $0 | **PASS** | both lanes forced to `0.0` and skip the budget gate; case-insensitive |
| Quote attached to the plan | **PASS** | `quote` event emitted before any spoke is built, `plan["quote"]` set, persisted on the assistant message and round-trips out of SQLite |
| `would_exceed` uses the ledger | **PASS** | `assert_budget` sums `usage_events` in SQL; inserting, ageing, and deleting rows moves the flag |

Release gate stays green: `python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve`
→ **28 tests, OK**. Probe suite `python3 -m unittest atelier.tests.evolve.test_opus_01`
→ **16 tests, OK (1 expected failure)** — the expected failure pins gap G3 below and will flip
to "unexpected success" the moment it is fixed.

## Detail behind each PASS

**Unknown ≠ free.** `is_priced()` returns true only for an exact `(provider, model, unit)` row or a
provider wildcard row, so a model the table has never heard of cannot claim to be priced.
`quote_run` then charges `conservative_usd = 0.04 * count + 0.01` instead of the fallback estimate,
marks `priced:false`, and the per-line `breakdown` carries its own `priced` flag. An entirely unknown
provider (`anthropic`) also fails safe: `priced:false`, non-zero hold. The hold scales with `count`.

**Local lanes.** `demo` and `ollama` quote `$0.00` with `priced:true` and never call `assert_budget`,
so a thread already $999 over budget still quotes free locally — correct, since neither lane bills.

**Quote rides with the plan.** `Conductor.run` quotes at the `brief` phase, before `build_spoke`, and
raises `BudgetExceeded` on `would_exceed` — which `server.py` maps to HTTP 402. `plan["quote"]` is a
5-key subset (`estimated_usd`, `priced`, `provider`, `image_model`, `count`) and `_summarize` renders
a `Quote: $x.xxxx (priced|unpriced conservative)` line into the stored assistant message.

**Ledger-backed budget.** `spent_since` sums `estimated_usd` from `usage_events`; daily is a rolling
24h window across all threads, thread budget is all-time for that thread. Both were exercised by
mutating rows directly: deleting the row clears the flag, a row aged past 24h drops out of the daily
window, and a 400-day-old thread row still counts against the thread cap.

## Gaps found (nothing applied)

**G1 — the quote holds one image, the weave can bill eight. (highest value)**
`quote_run` is called with `count = _wants_variants(prompt, variants) or 1`, i.e. 1 unless variants
were requested. The planner's reply is parsed *after* the quote, and the weave loop runs
`weave_items[:4]` with `count = min(item.count, 2)` per item — up to 8 images. Verified: a 4-item
plan produced 8 artifacts against `plan["quote"]["count"] == 1`. Per-image `usage.record` still calls
`assert_budget`, so a paid run fails closed partway rather than overspending, but the number the user
approved can be 8× low and the failure lands mid-weave. Smallest fix: after the plan is parsed,
re-quote with the real fan-out, emit a second `quote` event, and re-check the budget — or clamp the
weave to the quoted count.

**G2 — the Gemini image model the app actually calls has no price row.**
`image_model_for("gemini")` returns `gemini-2.5-flash-image`, which is absent from `COST_TABLE`
(the table has `gemini-3-pro-image`, `gemini-3.1-flash-image`, `imagen-*`). Every Gemini image quote
is therefore `priced:false` and falls to the $0.04/image floor. That floor is *below* both real Gemini
image prices: 4 images quote $0.17 versus $0.268 at `gemini-3.1-flash-image` and $0.536 at
`gemini-3-pro-image`. The "conservative" number is not conservative. Fix: add a row for the model the
code calls, and raise the unpriced floor to at least the most expensive known image price.

**G3 — ollama's `breakdown` contradicts its own total.**
`("ollama", "*", "images")` is missing from `COST_TABLE`, so `estimate_usd` returns the $0.04/image
guess; the images row reads `$0.08` at count 2 while the headline total is forced to `$0.00` and
`image_priced` is forced true by the `provider in {"demo","ollama"}` special case. Today's UI only
shows the total, so nothing visibly breaks, but the payload is internally inconsistent for any surface
that renders the breakdown. Fix: add `("ollama", "*", "images"): 0.0` and drop the special case from
`quote.py` so honesty comes from the table.

**G4 — two copies of the image-model table, already drifted.**
`quote.image_model_for` and `conductor._image_model` duplicate the same mapping and disagree for
ollama (`llama3.2` vs `demo-svg`), so an ollama quote names a model the weave will never call. Fix:
`conductor` should import `image_model_for`.

**G5 — `POST /api/quote` drops the connection on a bad `count`.**
`count=int(body.get("count") or body.get("variants") or 1)` sits outside any try block; `{"count":"abc"}`
raises `ValueError` inside `do_POST` and the client gets `RemoteDisconnected` with no HTTP response.
The `/threads/:id/run` route does the same `int()` *inside* its try and correctly returns 500. Fix:
parse and clamp defensively, return 400. (Float counts and 1e9 already coerce and clamp fine.)

**G6 — the plan card never shows the quote.**
`renderPlan` in `app.js` renders intent, mode, route and weave steps only; `plan.quote` is dropped.
The cost only reaches the user through the Quote button's status line and the summary message text.
`plan["quote"]` also omits `would_exceed`, `reason` and `conservative_usd`, so a persisted plan cannot
show that it was near the cap.

**G7 — model strings are not normalized.**
`" gpt-4o-mini "` misses the table and quotes as unpriced. Fails in the safe direction, but a stray
space silently turns a priced model into a $0.05 hold. Strip/casefold before lookup.

**G8 — price staleness is invisible.**
`PRICES_AS_OF = "2026-08-21"` is not returned in the quote payload, so neither the UI nor a caller can
warn that the table is old. Surfacing `prices_as_of` alongside `daily_budget_usd` is a one-line change.

**Minor.** `runBody()` never sends `capability`, so chat-only modes are quoted with an image charge;
an unknown paid provider quotes `image_model: "demo-svg"`, which is a misleading label for a lane that
will fail closed anyway.

## Reproduce

```bash
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve   # release gate, 28 OK
python3 -m unittest atelier.tests.evolve.test_opus_01                    # this audit, 16 OK (1 xfail)
```
