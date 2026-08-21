# ACCEPTANCE_CHECKLIST.md — Atelier Helix component acceptance

Component-level acceptance for the pieces this harness covers (store,
conductor parse, routing, usage ledger, demo loom, canvas pin). Product-level
acceptance lives in `01-product-spec/ACCEPTANCE.md`; this checklist is what a
release engineer runs before trusting those M-items to the machinery.

Every automated item names its verifying test. Run everything with:

```bash
cd /tmp/atelier-fable/10-eval
python3 test_helix.py -v        # unit suite (58 tests)
python3 test_helix.py --eval    # qualitative scorecard (target: 40/40)
```

Status column reflects the 2026-08-21 run against the live fleet components.

## 1. Store (04-helix-arch/schema.sql)

- [x] Schema loads and is idempotent (safe to re-run every statement) — `StoreSchemaTests.test_schema_loads_idempotently`
- [x] Project slugs validated at the store layer — `test_project_slug_is_validated`
- [x] I3: messages are append-only (no update, no delete) — `test_messages_are_append_only_i3`
- [x] I4: artifact content/provenance frozen; annotations editable — `test_artifact_provenance_is_frozen_i4`
- [x] I5: an artifact board node must reference an artifact — `test_canvas_pin_requires_artifact_i5`
- [x] I6: at most one active brand kit per project — `test_single_active_brand_kit_i6`
- [x] I8: usage_events append-only; cost never negative — `test_usage_events_are_append_only_i8`, `test_usage_cost_cannot_be_negative`
- [x] v_board_scene projects pins with geometry; unpin never deletes matter — `test_canvas_pin_appears_in_board_scene`

## 2. Conductor parse (05-conductor/conductor.py)

- [x] PROTOCOL.md §2 worked example parses verbatim — `ConductorParseTests.test_protocol_worked_example_parses`
- [x] Fenced/prose-wrapped JSON tolerated; pure prose rejected — `test_tolerates_fence_and_prose`, `test_rejects_unparseable_text`
- [x] Every §2 violation raises `PlanParseError` (14 cases: protocol, reading, steps, ids, craft, craft/kind, names, acceptance, needs, self-need, token-without-need, cycle, handoff x2) — `test_rejects_*`
- [x] `order_steps` is topological and cycle-loud — `test_order_steps_is_topological`, `test_rejects_dependency_cycle`
- [x] Critique envelope: accept/revise verdicts enforced; revise requires a blocker; bad severity rejected — `test_critique_*`

## 3. Routing (ROUTING.md rules)

- [x] Rule order holds on the worked example (compose→openai, render→image, image-consumer→gemini) — `RoutingTests.test_worked_example_follows_the_rule_order`
- [x] All four launch fixtures route cleanly: required lanes used, no `video`/`audio`/`3d` lane, no unrouted step — `test_every_fixture_plan_routes_cleanly`
- [x] Image emission and image lane always agree; `analyze-visual` always multimodal — `test_lane_rules_hold_for_every_fixture_step`
- [x] Registry missing a lane fails before any step runs — `test_registry_missing_a_lane_fails_before_any_step_runs`
- [ ] Rule 4 (long-source ≥ 8,000 chars → gemini) exercised by a fixture — **gap**, see EVAL.md §8.1

## 4. Usage ledger (08-security-quota/usage.py)

- [x] Token cost math matches the price table — `UsageLedgerTests.test_token_cost_math`
- [x] Unknown models: lenient None / strict raise — `test_unknown_model_lenient_none_strict_raises`
- [x] Negative quantities and empty units rejected — `test_negative_quantities_rejected`, `test_empty_units_rejected`
- [x] Events persist across reopen; thread/provider filters work — `test_record_persists_across_reopen`, `test_thread_and_provider_filters`
- [x] Key-shaped strings scrubbed from metadata (`sk-…`, `AIza…`, bearer) — `test_metadata_secrets_are_scrubbed`
- [x] Daily and per-thread budget caps block *before* the call; negative projections rejected — `test_budget_guard_*`
- [x] Demo runs record priced zero-cost events (no unpriced rows) — `test_demo_events_cost_zero_and_are_priced`

## 5. Demo loom — staged pipeline (helix_ref.py reference runner)

- [x] All four fixtures run brief→route→weave→pin with **no API keys in env and sockets blocked** — `DemoLoomTests.test_all_fixtures_run_offline_without_keys`
- [x] `conductor-manifest/1` contract: sha256/bytes match disk, lanes+spokes named per step, PNG artifacts valid — `test_manifest_matches_protocol_and_disk`
- [x] Source data flows through `[[token]]` substitution into artifact bytes (legal-directory names and phone number) — `test_factsheet_content_flows_through_tokens`
- [x] Reruns with fixed run id + clock are byte-identical — `test_reruns_are_byte_identical`
- [x] Every spoke call lands in the usage ledger (planner + one per step), cost 0 — `test_every_spoke_call_lands_in_the_ledger`
- [x] Thinking mode critiques and records a scorecard — `test_thinking_mode_critiques_and_accepts`
- [x] Mend semantics: blocker-flagged step re-runs exactly once, revision=1, others untouched — `test_thinking_mode_mends_blockers_exactly_once`
- [ ] Same assertions passed by the **real** end-to-end runner (05 `Conductor.run` wired to 07 spokes) — **pending integration**, see EVAL.md §8.2

## 6. Media loom demo mode (07-loom/loom.py)

- [x] Provider resolution falls back to `demo` when no keys configured — `LoomDemoModeTests.test_provider_resolution_defaults_to_demo_without_keys`
- [x] Demo images render offline with provenance sidecars (`provider: demo`) — `test_demo_images_render_offline_with_provenance_sidecars`
- [x] Demo brief expansion deterministic and schema-complete — `test_demo_brief_is_deterministic_and_complete`
- [x] Live provider without key raises `MissingKeyError` before any network I/O — `test_live_provider_without_key_fails_loud_before_network`
- [x] Video never auto-routes to a paid backend — `test_video_never_auto_routes_to_a_paid_backend`

## 7. Canvas pin (cross-component)

- [x] Demo-run manifest artifacts register in the store and pin to a board; `v_board_scene` shows every pin with geometry — `CanvasPinIntegrationTests.test_demo_run_artifacts_pin_to_the_board`
- [ ] Board UI (06-board-ui) renders `v_board_scene` content — **manual check**: open `06-board-ui/index.html`, confirm pinned artifacts appear and drag updates x/y only

## 8. Harness quality gates

- [x] Suite is runnable with zero fleet components present (falls back to `helix_ref.py`; 31 run / 27 skip, exit 0)
- [x] Suite auto-binds to real components when present (58/58, 0 skips on 2026-08-21)
- [x] Mutation check: a conductor that misroutes image work to a text lane makes the routing tests fail (10 failures observed) — tests are not vacuous
- [x] Qualitative scorecard reproducible via `--eval` (40/40 on 2026-08-21)
- [x] No file under `/workspace` modified; all outputs under `/tmp/atelier-fable/10-eval/`

## Sign-off gate

Ship the component set when: every automated box above is checked by a green
run of `python3 test_helix.py`, `--eval` reports ≥ 36/40 with no dimension at
0, and the two pending items (rule-4 fixture, real end-to-end runner) are
either closed or explicitly waived in the release notes.
