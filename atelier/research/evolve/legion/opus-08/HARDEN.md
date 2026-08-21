# ROUND 16 — Budget pre-call gate + HTTP 402 (opus-08)

**Verdict: PASS.** The round-16 claim ("Pre-call quote + HTTP 402") holds on the live
tree. A paid weave is priced and refused *before* any spoke is constructed, and the
server maps the refusal to `402 budget_exceeded`. The gate is real, but it is a
single-shot estimate with no hold, so it does not bound spend once a run is under way.

Verified against `atelier/helix/usage.py`, `atelier/helix/quote.py`,
`atelier/helix/conductor.py`, `atelier/server.py`, `atelier/web/app.js`.
Evidence tests: `atelier/tests/evolve/test_opus_08.py` (21 tests, green).

## 1. The ceiling — `usage.assert_budget`

```99:107:atelier/helix/usage.py
def assert_budget(memory, *, thread_id: Optional[str] = None, extra_usd: float = 0.0) -> None:
    day_start = time.time() - 86400
    daily = spent_since(memory, since_ts=day_start) + extra_usd
    if daily > DAILY_BUDGET_USD:
        raise BudgetExceeded(f"daily budget ${DAILY_BUDGET_USD:.2f} exceeded (${daily:.4f})")
    if thread_id:
        thread = spent_since(memory, since_ts=0, thread_id=thread_id) + extra_usd
        if thread > THREAD_BUDGET_USD:
            raise BudgetExceeded(f"thread budget ${THREAD_BUDGET_USD:.2f} exceeded (${thread:.4f})")
```

Two ceilings: a rolling-24h global total (`ATELIER_DAILY_BUDGET`, default $10) and a
lifetime per-thread total (`ATELIER_THREAD_BUDGET`, default $2). `extra_usd` is the
prospective cost, so the check is genuinely *pre*-spend when the caller supplies it.
Comparison is strict `>`: landing exactly on the ceiling is allowed
(`test_ceiling_is_strict_greater_than`).

## 2. The quote — `quote_run(...)["would_exceed"]`

```74:82:atelier/helix/quote.py
    would_exceed = False
    reason = ""
    if memory is not None and provider not in {"demo", "ollama"}:
        try:
            usage.assert_budget(memory, thread_id=thread_id, extra_usd=billed)
        except usage.BudgetExceeded as exc:
            would_exceed = True
            reason = str(exc)
```

`billed` is the priced estimate when every leg of the weave has a `COST_TABLE` row, and
a conservative `0.04 * count + 0.01` hold when any leg is unpriced
(`quote.py:66-72`). So an unknown model is held against the budget rather than treated
as free — `test_unpriced_model_gates_on_conservative_hold`. The free lanes (`demo`,
`ollama`) are never flagged, and a quote called without `memory` can never flag
(`test_quote_without_memory_cannot_gate`); `/api/quote` does pass `app.memory` and
`thread_id`, so the endpoint's verdict matches the conductor's.

## 3. The pre-call gate — before the spoke exists

```133:145:atelier/helix/conductor.py
        q = quote_run(
            provider=provider,
            model=model,
            prompt=prompt,
            count=max(1, _wants_variants(prompt, variants) or 1),
            memory=self.memory,
            thread_id=thread_id,
        )
        emit("quote", quote=q)
        if q.get("would_exceed"):
            raise usage.BudgetExceeded(q.get("reason") or "budget exceeded")

        spoke = build_spoke(provider, self.keyring)
```

Ordering confirmed by test, not just by reading: with `build_spoke` patched to a
recorder, an over-budget paid run raises and the recorder is never called — no spoke
object, no planner chat, no image call, no artifact row, no board node
(`test_no_spoke_is_built_when_the_quote_would_exceed`). The `quote` event is emitted
before the raise (`test_quote_event_is_emitted_before_the_raise`), and the demo lane
still weaves at 3x the daily ceiling (`test_demo_lane_still_weaves_over_budget`).

## 4. The wire — HTTP 402

```369:371:atelier/server.py
            except BudgetExceeded as exc:
                _json(self, 402, {"error": str(exc), "code": "budget_exceeded", "ok": False})
                return
```

`402` / `code: budget_exceeded` / `ok: false`, matching `CONTRACT.md:30`. It fires for
`?stream=1` too — the conductor runs to completion before the SSE writer starts, so an
over-budget streaming run gets a JSON 402 rather than a half-open event stream
(`test_stream_run_also_402s_instead_of_opening_sse`). After a 402 the board is still
empty (`test_run_over_budget_returns_402_budget_exceeded`).

## Remaining holes

1. **The UI does not block Weave on `quote.would_exceed`.** `app.js:315-325` renders
   "— would exceed budget" on the Quote button, and `app.js:327-348` (the Weave button)
   never reads that flag: it posts the run and relies on the server's 402 landing in the
   status line. Quoting is also entirely optional, so the common path is to weave first
   and learn about the budget from an error. Server-side is the only enforcement point
   — correct as defense-in-depth, wrong as the *first* line of defense.
2. **The pre-call quote can be a fraction of the real spend.** It prices
   `max(1, variants)` images, but the planner's returned plan is walked as
   `weave_items[:4]` with `count` up to 2 each (`conductor.py:216-226`) — up to 8 images
   against a 1-image hold. `test_multi_item_plan_outspends_the_pre_call_quote` drives a
   two-image plan through a $0.05 headroom: both images are generated and billed by the
   provider, the second `usage.record` raises, and the run 402s mid-flight.
3. **The mid-run gate loses the money it refuses.** `usage.record` calls
   `assert_budget` *before* `memory.add_usage` (`usage.py:110-121`), so the spend that
   broke the ceiling is never written to the ledger
   (`test_record_drops_the_row_it_was_asked_to_write`). The provider still invoices it;
   the next run's gate reads a total that is low by exactly the overrun.
4. **A mid-run 402 leaves debris.** The artifact row and the file on disk are written
   before `usage.record` (`conductor.py:265-286`), so a run killed at image two keeps
   both artifacts while the caller sees only an error. The 402 body also drops the
   `events` list and the quote, so the client cannot show the estimate or the remaining
   headroom (`test_402_body_carries_no_quote_for_the_client`).
5. **No hold, so the gate is TOCTOU.** `assert_budget` reads `SUM(estimated_usd)` and
   returns; nothing is reserved between the check and the eventual `record`. The server
   is a `ThreadingHTTPServer`, so N concurrent runs all read the same pre-spend total
   and all pass. Bounding concurrent spend needs a reservation row released on
   completion, not a read-only sum.
6. **Budgets are import-time constants** (`usage.py:15-16`), so
   `ATELIER_DAILY_BUDGET` / `ATELIER_THREAD_BUDGET` must be set before the process
   imports the module; there is no per-project, per-provider, or per-key ceiling, and no
   API to change one at runtime.
7. **The daily window is a rolling 24h, shared globally.** One thread burning $10 blocks
   every project and every provider for the next day, and there is no calendar-day reset
   a user could reason about.
8. **The conservative hold is optimistic for expensive unpriced models.** $0.04/image +
   $0.01 is below real rows already in the table (`gemini-3-pro-image` at $0.134), so an
   unpriced model in that class under-holds by ~3x. The conductor also always quotes
   `capability="image"` (it never forwards a chat-only capability), so chat-only runs
   over-hold — harmless, but it means the quote shown is not the quote enforced.
9. **A blocked run still mutates the thread.** `add_message` runs at
   `conductor.py:131`, before the gate, so a 402'd prompt is persisted as a user message
   with no assistant reply.

## Reproduce

```bash
python3 -m unittest atelier.tests.evolve.test_opus_08      # 21 tests, OK
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve   # release gate, OK
```
