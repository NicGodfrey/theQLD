<!-- Conductor note: this is the missing Opus-01 product slice.
Scored against 1bfa56d, before sequential R4–R7. Later rounds already
closed download slugs, upload-as-parent, camera Home/Fit, and a visible
plan/critic card. Treat remaining PNG/PDF export, paid-lane brand kit,
and explicit board selection as still open. -->

# GAPS.md — Atelier (live Helix) → 成品可用

**Author:** Opus#1 of 10 · **Date:** 2026-08-21
**Scored against:** `/workspace` @ **`1bfa56d`** ("Keep conversations in project export and accept node
data.", 19:10:25 UTC). Every line number below is from that commit.
**Scope:** gap analysis from the live runtime in `/workspace/atelier/` to a *finished usable product* —
someone who is **not** a developer can install it, add their own API keys, and complete
**brief → generate → edit → export**.

**Method:** read every live file (`server.py`, `helix/`, `web/`) and the spec pack
(`research/fable5/01-product-spec/ACCEPTANCE.md`, `FEATURE_MATRIX.md`, `UX_FLOWS.md`,
`SYNTHESIS.md`), then **ran the live product** and drove the HTTP API end-to-end. Nothing under
`/workspace` was written: runtime redirected with `ATELIER_HOME` / `ATELIER_RUNTIME` into `/tmp`.

> **Note on a moving target.** I began against `6515594` (18:48 UTC). A hardening wave
> (`c6a1067` → `1bfa56d`) landed mid-analysis and changed 27 live files. I re-read and re-probed
> everything against `1bfa56d`; §1.1 records the before/after because the *shape* of the delta is the
> single most useful finding in this report.

---

## 0. 判定 / Verdict

> **Atelier now has a partial implementation of almost everything and a finished implementation of
> almost nothing.** Of the 27 M-items in `ACCEPTANCE.md`: **2 DONE, 15 PARTIAL, 9 MISSING** (+1 N/A,
> +the exit bar MISSING). The MVP exit bar (`ACCEPTANCE.md:51`) still cannot be executed, because its
> terminal step — PNG + PDF export — has no code path at all.

The user-visible loop today:

| Loop step | Status @ `1bfa56d` |
|---|---|
| **install** | ⚠️ still a developer task — no packaging anywhere in the repo; `python3 -m atelier` only works from the package parent |
| **keys** | ✅ genuinely good — env or UI, never echoed, official-host lock now enforced **at save time** (400), atomic 0600 write, symlink refusal |
| **brief** | ✅ works, and now quotes the spend before firing |
| **generate** | ✅ works and is now **fail-closed** — a keyless/invalid paid provider returns `422 auth` instead of minting a demo SVG that looks like a paid success |
| **edit** | ⚠️ the backend exists (refine-with-lineage, `parent_artifact_id`); the UI trigger is an **undocumented magic word** (`/spot|局部|edit this/i`) aimed at an **arbitrary target** (`web/app.js:309-311`) |
| **export** | ❌ **still no designer export** — you can download a raw `.svg` or a project `.zip` of JSON + raw artifacts. No PNG, no JPEG, no PDF, no scale, no dialog |

Three findings dominate, all of them *finishing* work rather than new subsystems:

1. **Export is archival, not usable.** `GET /api/projects/{id}/export` produces
   `project.json / board.json / threads.json / artifacts.json + artifacts/*.svg` (verified). That is a
   backup file. A designer needs a PNG or a print-ready PDF and can get neither. The loop still has
   no exit.
2. **Edit works but is undiscoverable and untargetable.** Verified: posting
   `parent_artifact_id` produces a child artifact with real lineage (`artifacts.parent_id`) and a
   composed spot-edit prompt. But the only way to reach it from the UI is to include the substring
   "spot" (or "局部", or "edit this") in your prompt, and the target is `state.lastArtifactId` —
   whichever image node happened to render last (`web/app.js:132`), **not** anything the user chose.
   There is still no selection state and no target confirmation anywhere in the product.
3. **The brand kit silently stops working the moment you pay.** `Conductor` now passes
   `palette=` and `title=` into `image()` (`helix/conductor.py:266-271`) and `DemoSpoke` honours them
   (`helix/loom.py`, `spokes/base.py:86-93`). `OpenAISpoke.image` and `GeminiSpoke.image` accept
   `**kwargs` and **ignore both** (`spokes/openai_spoke.py:70-85`). So StyleLock visibly works in
   demo mode and does nothing on every real engine — the worst possible failure mode for the feature
   that is supposed to justify the product commercially.

**成品可用 gate:** items **1–7** of §7. That set needs **zero new dependencies** and **zero new model
vendors** — it is wiring, format conversion, and one selection model.

---

## 1. 证据 / What I actually ran

```
$ python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve   → 32 tests, OK
$ ATELIER_PORT=8792 python3 -m atelier                                    → /api/health ok, evolve_rounds: 20
```

| Probe | Result @ `1bfa56d` | Reading |
|---|---|---|
| `POST /api/quote` `{provider:openai,count:4}` | `estimated_usd 0.1603, priced true`, per-unit breakdown, daily/thread caps echoed | cost preview now **exists** |
| `POST /run` `provider=openai`, **no key** | **`422 {"code":"auth"}`** | **fail-closed — the false-provenance bug is fixed** |
| `POST /api/keys` `base_url=https://evil.example.com` | **`400 {"code":"unofficial_host"}`** | host lock now enforced at save time |
| `POST /run` `variants=4` (demo) | 4 artifacts, 4 nodes, `plan.variants=4`, 2-col grid, `quote` in the message | 4-up works — but auto-pins, no pick/keep |
| `POST /run` `parent_artifact_id=…` | `plan.spot_edit.parent_id` set, child `artifacts.parent_id` set, prompt composed from parent | refine + lineage works |
| `GET /api/artifacts/{id}?download=1` | `filename="…​.svg"`, `X-Content-Type-Options: nosniff` | filename fixed; **no format conversion** |
| `GET /api/projects/{id}/export` | zip: `project.json, board.json, threads.json, artifacts/*.svg, artifacts.json` | archive, not a designer export |
| `POST /api/projects/{id}/undo` | `{"undone":true,"action":"add_node"}` | undo exists — **only** for `add_node` |
| `POST /api/nodes/{missing}` | **`HTTP 000`** — connection dropped, `TypeError` in `store.get_node` | **still crashes** |
| `GET /api/providers` | `404` | model picker is still a free-text box |
| packaging | none at `/workspace` or `/workspace/atelier` | install still a developer task |
| `fit` / node-`DELETE` in `web/app.js` | 0 occurrences each | no fit-to-content; `DELETE` endpoint exists but is unreachable from the UI |

Earlier snapshot artefacts kept for the record: `/tmp/atelier-opus/live-ui.png` (UI @ `6515594`),
`/tmp/atelier-opus/probe_budget.py` (the orphan-artifact probe, now closed by the pre-flight quote).

### 1.1 What the hardening wave changed — and what it tells us

| | @ `6515594` (18:48) | @ `1bfa56d` (19:10) |
|---|---|---|
| DONE | 2 | **2** |
| PARTIAL | 7 | **15** |
| MISSING | 18 | **9** |
| N/A | 1 | 1 |

**Eleven M-items moved MISSING → PARTIAL. Zero moved to DONE.** Landed: `/api/quote` with
pre-flight budget refusal (`402`), fail-closed paid providers, camera pan/zoom persisted per project,
`variants=4`, `parent_artifact_id` refine + `artifacts.parent_id` lineage, `undo_log`,
`text` node type, base64 upload + drag-drop, project-zip export, `DELETE /api/nodes/{id}`,
SSE `?stream=1`, an `RLock` + WAL + `busy_timeout` around the store, atomic 0600 keyring writes with
symlink refusal, `safe_under()` path containment, `is_priced()` so unknown models are no longer
treated as free, and a `Host`-header check on loopback binds. Tests went 7 → 32.

That is real, well-aimed work. It also means **the remaining backlog is almost entirely
"finish the last 20%" rather than "build the thing"** — which is why the ranked list in §7 is short
on new subsystems and long on completion.

---

## 2. A scope conflict that must be resolved before M-6 can be scored honestly

`ACCEPTANCE.md` was written against a **hosted, credit-metered SaaS** (M-3.3 "credit cost",
M-6.2 "free tier … watermarked exports", M-6.3 "paid tiers", M-6.4 "credit ledger"). `SYNTHESIS.md:8`
and `ARCHITECTURE.md:3-12` state the shipped product is a **local BYOK studio** with **no Atelier
billing at all** — spend lands on the user's own provider account, gated by `ATELIER_DAILY_BUDGET` /
`ATELIER_THREAD_BUDGET` (`helix/usage.py:15-16`).

Both cannot be the ship target. Re-specification used for scoring below:

| Original M-item | BYOK re-spec |
|---|---|
| M-3.3 credit cost before generation | **USD estimate** before generation — now implemented as `/api/quote` — plus an in-UI, non-env budget cap |
| M-6.2 free tier / watermark / Direct-only | **Out of scope.** Demo mode is the free tier and needs no watermark |
| M-6.3 commercial-rights statement | **Keep, re-aimed:** the export dialog must state that output rights follow the *provider's* ToS (OpenAI / Google), because Atelier grants nothing |
| M-6.4 credit ledger | **USD ledger**, per turn, engine + action + cost |

Leaving this unresolved is itself a shipping risk: nobody can say whether the product is done.
**Ship item #0 is a document, not code.**

---

## 3. Scorecard — M-items (27 + exit bar)

`DONE` = passes as written, or as re-specified in §2. `PARTIAL` = a real code path exists but fails
the stated acceptance test. `MISSING` = no code path. Δ marks movement since `6515594`.

### M-1 Project & canvas

| # | Item | Score | Evidence |
|---|---|---|---|
| M-1.1 | new project → empty canvas ≤2 s; install → first generation ≤2 min, no required onboarding | **PARTIAL** | project create is instant (`server.py:313-317`); but "New project" is a `window.prompt()` (`web/app.js:262`), not the 3-field modal of `UX_FLOWS.md:18-21`; no example-brief chips (`UX_FLOWS.md:22-23`); **install is not a 2-minute path** (§6.1) |
| M-1.2 | ≥200 nodes @ 60 fps pan/zoom | **PARTIAL** Δ | camera landed: wheel-zoom clamped 0.25–3, drag-pan, persisted via `POST /api/projects/{id}/camera` (`web/app.js:170-197`, `helix/store.py` `set_camera`). Missing: **fit-to-content** and a reset control (`camReadout` is a passive `<span>`), and `refreshBoard` still does `innerHTML=""` and re-requests every image on **every** turn (`web/app.js:118-144`), so the 200-node/60 fps bar is untested and unlikely |
| M-1.3 | no project cap | **DONE** | `store.py`, no limit |
| M-1.4 | ≥2 threads/project, each with an **isolated context ledger** | **PARTIAL** | threads work; **there is still no ledger** — `Conductor.run` builds `planner_messages` from the current prompt + brand kit only (`helix/conductor.py:150-156`) and never reads `list_messages` or `list_nodes` |

### M-2 Chat & agent (Helix)

| # | Item | Score | Evidence |
|---|---|---|---|
| M-2.1 | visible, **editable** plan card; run executes remaining steps | **PARTIAL** Δ | `renderPlan` now shows intent, mode, route, and up to 4 weave steps as an `<ol>` (`web/app.js:98-116`). It is **read-only** — no delete, no reorder — and `/run` is still one atomic call, so there is no plan → confirm → execute split |
| M-2.2 | plan latency ≤15 s | **MISSING** | phase events exist (`conductor.py:123-130`) but carry **no timestamps**; `usage_events` has no latency column. Unmeasurable ⇒ unpassable |
| M-2.3 | ≤3 clarifying questions, grouped, "use defaults" escape | **MISSING** | `PLANNER_SYSTEM` has no `ask`/`questions` field (`conductor.py:25-38`); no question surface |
| M-2.4 | Direct mode: first pixels <15 s, **no plan** | **PARTIAL** | `fast` still makes a full planner round-trip before generating (`conductor.py:158-159`), so Direct is not direct; latency unmeasured |
| M-2.5 | mode toggle every turn, draft prompt preserved | **DONE** | `#mode` read per run (`web/app.js:305`), never clears `#prompt`. Caveat: the control is still visually illegible (§6.7) |
| M-2.6 | referring expressions → correct node ≥90%, target shown before edit | **MISSING** | no selection state anywhere. The one targeting mechanism is a regex on the prompt text pointing at the last-rendered node (`web/app.js:309-311`) — an unannounced heuristic with no confirmation chip, i.e. the opposite of the `UX_FLOWS.md:39` requirement |

### M-3 Generation

| # | Item | Score | Evidence |
|---|---|---|---|
| M-3.1 | ≥2 image engines behind a Router; auto-choice **logged with reason**; manual override | **PARTIAL** | 2 paid engines + demo; unknown providers now rejected up front (`conductor.py:132-133`, `KNOWN_PROVIDERS`). But routing is still "whatever the planner LLM wrote", **no reason is logged**, `ROUTING.md`'s rule ladder is research-only, and the manual override is still **broken for images**: the user's `model` box feeds `chat()` only — `image()` always gets `_image_model(route_provider)` (`conductor.py:263`), so `dall-e-3` silently becomes `gpt-image-1` |
| M-3.2 | engine name on every node, in chat, in export metadata | **MISSING** | `GET /api/projects/{id}/board` still returns nodes without joining artifacts (`server.py:225-229`), so the UI **cannot** show the engine; node caption is still the prompt (`web/app.js:137`); the chat line reports the *chat* route, not the image engine (`conductor.py:400`); no export metadata. **The good news:** fail-closed means this is now merely absent, not false — the demo-SVG-labelled-as-OpenAI bug is fixed |
| M-3.3 | cost shown **before** every generation; cannot fire without it; failures refunded | **PARTIAL** Δ | big improvement: `POST /api/quote` (`helix/quote.py`), a **Quote** button (`web/app.js:315-325`), pre-flight `assert_budget` **before** the spoke call and a re-quote when the plan changes the image count (`conductor.py:135-145, 208-222`), `BudgetExceeded → 402` (`server.py:405-407`), and the quote is echoed in the run message. Remaining: the quote is **not a gate** — **Weave** fires without it; no refund/rollback concept; caps still env-only (§6.13) |
| M-3.4 | Pick grid of 4 variants + rationale, Tab cycling, recoverable variant stack | **PARTIAL** Δ | `variants=4` produces 4 renders of one prompt in a 2-column grid (`conductor.py:86-94, 190-201`; verified 4/4). But they are **auto-pinned** to the board — no grid, no per-variant rationale, no `Tab`/`Enter`, no keep/discard, no recovery of unkept variants |
| M-3.5 | 1 video engine (t2v + i2v), ≤10 s, 1080p, MP4 | **MISSING** | no video in live code. Research has `DemoVideo`/`SoraVideo`/`VeoVideo` (`07-loom/loom.py:928,955,1007`) — unwired |

### M-4 Editing

| # | Item | Score | Evidence |
|---|---|---|---|
| M-4.1 | Spot Edit: click→auto-mask→instruction, outside-mask byte-identical, ≥85% mask rate, manual brush | **PARTIAL** Δ | the backend refine exists and is honest about lineage: `parent_artifact_id` → `plan.spot_edit`, composed prompt, `artifacts.parent_id` (`conductor.py:223-227, 239-244, 293`; verified). But it is **whole-image regeneration** — no mask, nothing byte-identical — and the UI trigger is the magic-word regex on an arbitrary target (`web/app.js:309-311`). Capability: partial. Usability: ~zero |
| M-4.2 | text layers: click-to-edit real text, preserves font/size/position | **PARTIAL** Δ | a `text` node type and a **Text layer** button now exist (`server.py:336-348`, `web/app.js:356-364`). But it is a `window.prompt()` producing a static div on the board — not click-to-edit, not attached to an image, no font/size/colour from the kit, not exported as vector text |
| M-4.3 | background removal as a one-click canvas verb | **MISSING** | — |
| M-4.4 | node undo ≥50 steps; snapshot every agent turn; restore ≤5 s | **PARTIAL** Δ | `undo_log` + `POST /api/projects/{id}/undo` (`store.py` `push_undo`/`undo`, `server.py:333-335`; verified). But `undo` handles **only `add_node`** — a node *move* or *delete* is unrecoverable, `update_node` is still a destructive `UPDATE`, there is no ≥50-step guarantee, and there is no project snapshot/restore at all |

### M-5 Brand (StyleLock)

| # | Item | Score | Evidence |
|---|---|---|---|
| M-5.1 | kit = logos (SVG/PNG) + palette (hex **+ roles**) + fonts + tone; **multiple kits** | **PARTIAL** | still one free-form JSON blob per project in a raw `<textarea>` (`web/index.html:44-48`). No schema, no role labels, no font refs, no logo binding, **one kit maximum**. `JSON.parse` is still uncaught (`web/app.js:298`) → a typo silently discards the save |
| M-5.2 | project-default selector **and** per-turn `@` override | **PARTIAL** | project default is injected into the planner prompt (`conductor.py:151`, `_brand_block:391-394`). No selector (nothing to select between), no `@` mention, no per-turn override |
| M-5.3 | ΔE ≤10 on ≥90% of a 50-gen benchmark; critic flags violations | **MISSING** | `palette=` / `title=` are now passed to `image()` (`conductor.py:266-271`) and **only `DemoSpoke` honours them** (`spokes/base.py:86-93`, `loom.py` `demo_svg`). `OpenAISpoke.image` builds `{model, prompt, n, size}` and drops the rest (`spokes/openai_spoke.py:70-85`); `GeminiSpoke.image` likewise. So the kit reaches demo pixels and **no paid pixels**. The critic still receives `Artifacts: {len(artifacts)}` — *a number* (`conductor.py:333`) — so it structurally cannot check colour. No ΔE anywhere |
| M-5.4 | Shelf: upload once, `@` mention from another project | **PARTIAL** Δ | upload landed: `POST /api/projects/{id}/upload` (base64 JSON, ≤5 MB) + drag-drop and a file picker (`server.py:349-387`, `web/app.js:198-218`). But it is project-scoped with no workspace promotion, there is no `@` mention, and — critically — **an uploaded reference is never fed into any generation**; it only pins a node |

### M-6 Export & plans

| # | Item | Score | Evidence |
|---|---|---|---|
| M-6.1 | PNG (incl. transparent), JPEG, SVG, PDF-RGB; MP4 | **MISSING** | two real improvements — correct download extensions via `ext_for_mime` (`server.py:253`, `loom.py`) and a project archive `GET /api/projects/{id}/export` (`helix/exportzip.py`) — but **zero format conversion**. A demo artifact is SVG and stays SVG; paid artifacts are PNG and stay PNG. No JPEG, no PDF, no scale, no transparency control, no export dialog. The zip is a backup, not a deliverable |
| M-6.2 | free tier: credit grant, watermark, Direct-only | **N/A** per §2 | BYOK has no tiers |
| M-6.3 | rights statement in the export dialog | **MISSING** | no export dialog; no output-rights text anywhere in the studio |
| M-6.4 | ledger: per-turn history with engine, action, cost | **PARTIAL** | `usage_events` + `GET /api/usage` + real dated prices (`usage.py:19-58`), and the per-run quote now appears in the assistant message (`conductor.py:405-408`). But the UI still shows **one aggregate float** (`web/app.js`, `topMeta`); rows carry `thread_id`, not `message_id`, so exact per-turn attribution is not reconstructible |
| **Exit bar** | brief → plan → 4 variants → 2 Spot Edits → kit swap → PNG+PDF, ≤10 min, 5 external testers | **MISSING** | closer than before — plan card, 4-up, and refine all exist in some form — but the terminal **PNG+PDF step is impossible**, and "kit swap" is a no-op on every paid engine (M-5.3). Not runnable, therefore not timeable |

**Totals: DONE 2 · PARTIAL 15 · MISSING 9 · N/A 1** (+ exit bar MISSING) = 28.

---

## 4. Scorecard — P2-items

| # | Item | Score | Note |
|---|---|---|---|
| P2-1a | ≥4 image + ≥3 video engines; Router A/B win-rates logged | **MISSING** | 2 image, 0 video, no A/B logging. `03-keyring-spokes/spokes_anthropic.py` adds a 3rd *chat* provider only |
| P2-1b | keyframes / camera / cuts / 4K | **MISSING** | — |
| P2-2a | music + SFX, `sfx_`/`mus_` shelf labels | **MISSING** | research has a WAV chime generator (`07-loom/loom.py:497`), not music |
| P2-2b | TTS voiceover on video nodes | **MISSING live / research-complete** | `07-loom/loom.py:819,844` + `PIPELINES.md` §Pipeline 3 done and unwired |
| P2-2c | text/image→3D, GLB export | **MISSING** | not researched either |
| P2-3a | PSD with ≥3 editable layers | **MISSING** | blocked upstream — nothing in the pipeline produces layers. The new `text` node is a board annotation, not an image layer |
| P2-3b | PDF CMYK + configurable bleed | **MISSING** | blocked on M-6.1 (no PDF at all) |
| P2-4a | Fanout ≥7 platform sizes, one job | **MISSING** | size is still hardcoded `1024x1024` (`spokes/openai_spoke.py:71`) and not user-reachable |
| P2-4b | Sweep N-way single-variable strips | **MISSING** | `variants=4` is the seed of this, but it varies the *prompt suffix*, not a named variable |
| P2-4c | character consistency ≥5 gens, ≥70% same-person | **MISSING** | `image()` still has no image-input parameter, so uploaded references cannot condition a generation |
| P2-5a | shared workspaces + shared kits | **MISSING** | single-tenant by design (`04-helix-arch/ARCHITECTURE.md`) |
| P2-5b | public API, project/thread mgmt, generation, **keyed auth** | **PARTIAL** Δ | the REST surface is real and now has a `Host`-header guard on loopback binds, an `RLock`, and path containment (`server.py:107-115, 118-124`). But there is still **no authentication**: `_check_host` returns `True` unconditionally when `ATELIER_HOST` is non-loopback, so `ATELIER_HOST=0.0.0.0` exposes unauthenticated `POST /api/keys` (writes secrets) and `POST /run` (spends money) to the LAN |
| P2-5c | web-research step in Plan mode | **MISSING** | — |
| P2-5d | relax off-peak queue | **N/A** | correctly moot under BYOK |

**Non-goals:** no template library ✅ · no stylized-art specialization ✅ · "engines are always named"
— **now honest** (fail-closed removed the false-provenance case) but still **incomplete**: the engine
name appears nowhere on the node or in exports.

---

## 5. Gap detail — why it blocks 成品可用, severity, smallest fix vs research-complete fix

### G1. Export is archival, not usable  *(M-6.1, M-6.3)* — **BLOCKER**

*Why it blocks:* the two export paths both fail the designer. `?download=1` gives one raw artifact in
whatever format the engine happened to emit — for keyless/demo work that is an **SVG**, which no
client will accept as a deliverable and which Illustrator will open with a system-font substitution.
`GET /api/projects/{id}/export` gives a `.zip` of JSON plus raw artifacts — a backup file. There is no
PNG, no JPEG, no PDF, no scale, no transparency, no dialog, no rights line. The loop has no exit.

*Smallest fix (still zero dependencies):*
1. Make **PNG the canonical artifact**. Adopt the pure-stdlib PNG writer already sitting in research —
   `07-loom/loom.py:318` (`write_png`, `zlib` + `struct` only) and `:359`
   (`render_placeholder_png`) — so `DemoSpoke` emits PNG instead of SVG. This alone makes "export PNG"
   free for the keyless path, which is the path every first-time user takes.
2. `GET /api/artifacts/{id}/export?fmt=png|jpeg|pdf&scale=1|2|4`, with a human filename
   (`{project}-{node}-{WxH}.{ext}`). Keep SVG passthrough for genuinely vector artifacts.
3. **PDF-RGB is ~120 lines of stdlib** — a one-page PDF embedding the PNG/JPEG as an image XObject.
   No Cairo, no Pillow; consistent with the stdlib-only MVP policy
   (`09-oss-adapters/ADAPTERS.md:303-308`).
4. An **Export** button on every node (next to the existing Download link, `web/app.js:134-136`) plus
   one line of rights text: *"Output rights follow your provider's terms (OpenAI / Google). Atelier
   grants none of its own."*

*Research-complete fix:* export as a first-class service — full format matrix incl. transparent PNG
and vector-text SVG, XMP metadata embedding engine + prompt hash + project id (`UX_FLOWS.md:70`),
multi-node batch/zip, P2-3 layered PSD once the pipeline produces layers, PDF CMYK + bleed.

---

### G2. Edit is undiscoverable and untargetable  *(M-4.1, M-2.6)* — **BLOCKER**

*Why it blocks:* the machinery is there and it is good — `parent_artifact_id` produces a child
artifact with `parent_id` lineage and a prompt composed from the parent (verified). The *product*
around it does not exist. To edit, a user must (a) guess that typing the word "spot" changes the
request semantics, and (b) accept whatever `state.lastArtifactId` happens to be — the last image node
`refreshBoard` rendered (`web/app.js:132, 309-311`). No click-to-select, no highlight, no
"→ Logo v3" confirmation. A non-developer will never find this, and if they stumble into it, it will
edit the wrong node.

*Smallest fix:* introduce **selection**. Click a node → `state.selectedNodeId` + a visible ring;
send `parent_artifact_id` from the selection (never from a regex); render a target chip on the user's
message before the run (`UX_FLOWS.md:39`); add an explicit **Refine** button on the selected node so
the capability is discoverable without magic words. Call it *Refine*, not *Spot Edit*, until masks are
real — the current behaviour regenerates the whole image and the acceptance text promises
byte-identical pixels outside a mask (`ACCEPTANCE.md:33`).

*Research-complete fix:* true Spot Edit — segmentation auto-mask via an out-of-process worker (the
ComfyUI-over-HTTP pattern, `09-oss-adapters/ADAPTERS.md:155`), masked inpaint, byte-identical
composite outside the mask, manual brush fallback, and a real text-layer model so headlines are
vector text rather than pixels (`FEATURE_MATRIX.md:58`).

---

### G3. The brand kit does nothing on paid engines  *(M-5.3, M-5.1, M-5.2)* — **BLOCKER**

*Why it blocks:* StyleLock is the commercial differentiator. The plumbing was added but only
connected on one end: `Conductor` passes `palette=`/`title=` to `image()`
(`conductor.py:266-271`), `DemoSpoke` uses them (`spokes/base.py:86-93`), and
`OpenAISpoke.image`/`GeminiSpoke.image` swallow them in `**kwargs`
(`spokes/openai_spoke.py:70-85`). The result is the most expensive kind of bug: the feature
**demonstrates correctly with no key** and silently degrades to nothing the moment the user pays.
The critic that is supposed to flag violations still receives the string `Artifacts: 1`
(`conductor.py:333`), so there is no detection path either.

*Smallest fix:* (a) build a deterministic style suffix from the kit — hex list with role labels, font
names, tone — and append it to **every** image prompt for **every** provider (one function, called in
one place); (b) give the critic the actual image bytes through the Gemini multimodal path that already
exists for `image()` (`spokes/gemini_spoke.py:79-92` shows the inline-part shape); (c) replace the raw
JSON textarea with a real form — swatch + role rows, heading/body fonts, tone — per
`06-board-ui/UI_SPEC.md` §4.7, and **catch the `JSON.parse` throw** (`web/app.js:298`) so a typo does
not silently discard the save.

*Research-complete fix:* multiple kits with one active per project (`04-helix-arch/schema.sql:288`,
invariant I6; `activate` at `openapi.yaml:743`), logo/asset binding (`brand_assets`), `@`-mention
per-turn override, and a real ΔE-2000 pass over the output so `ACCEPTANCE.md:41` becomes a runnable
test instead of an aspiration.

---

### G4. The agent still has no memory  *(M-1.4, M-2.6)* — **BLOCKER**

*Why it blocks:* every turn is a cold start. `planner_messages` is built from the current prompt plus
the brand kit and nothing else (`conductor.py:150-156`); `list_messages` and `list_nodes` are never
read by the planner. "Same but darker", "make the logo bigger", "the second poster" cannot work even
in principle. This is also what makes G2 worth building: refine needs something to refine *against*.

*Smallest fix:* pass the last N turns plus a compact board inventory
(`node_id, type, engine, one-line prompt`) into the planner prompt; accept `selected_node_id` from the
UI; add `"target_node"` to the plan schema so the resolved target can be echoed as a confirmation
chip.

*Research-complete fix:* the Intent/Matter model — append-only messages with `rungs`
(`04-helix-arch/schema.sql:63-95, 206`), artifact lineage endpoints (`openapi.yaml:443`), named-entity
resolution over the ledger, board-as-disposable-projection (`SYNTHESIS.md:9`).

---

### G5. Installing it is a developer task  *(M-1.1)* — **BLOCKER for the stated audience**

*Why it blocks:* the target is "no required onboarding steps, ≤2 min to first generation". Reality:
`atelier.html:30` tells the user to run `python3 -m atelier` with **no download link, no clone
command, no `cd` instruction, and no Python version**. There is **no `pyproject.toml`,
`requirements.txt`, or `Makefile` anywhere in the repo** (verified). Run the command from any other
directory and you get `No module named atelier`. No browser auto-open, no port-conflict fallback, no
first-run key prompt.

*Smallest fix:* a `pyproject.toml` with an `atelier` console script; `webbrowser.open()` on boot;
port fallback if 8765 is taken; honest copy on `atelier.html` ("Requires Python 3.11+.
`pipx install atelier-studio` → `atelier`"); and a first-run empty state that says which keys to get
and where — the copy already exists inside an exception string (`spokes/openai_spoke.py:21-24`), it
just needs to be on screen before the failure rather than after.

*Research-complete fix:* per-OS single-file builds or a Docker one-liner, plus
`GET /api/providers/{id}/verify` (`04-helix-arch/openapi.yaml:879`) so **Save key** confirms the key
works immediately, instead of the user discovering it three clicks later as a `422`.

---

### G6. Provenance is honest but invisible  *(M-3.2)* — **MAJOR** (was a blocker; fail-closed fixed the lying half)

*Why it still matters:* the run message reports `Route: {chat_provider} / {chat_model}`
(`conductor.py:400`) — the *planner* model, not the *image* engine that made the pixels. Nodes carry
no engine at all, and cannot: `GET /api/projects/{id}/board` returns nodes without joining artifacts
(`server.py:225-229`). Exports carry no metadata. For a BYOK product, "which engine made this and
what did it cost" is the core reporting requirement.

*Smallest fix:* join `artifacts.provider/model/parent_id` into the board payload; render an engine
chip on each node beside the existing Download link; report the **image** model in the summary
alongside the planner model.

*Research-complete fix:* the `conductor-manifest/1` envelope (`05-conductor/PROTOCOL.md` §4) — per
step: lane, spoke, model, sha256, byte count — persisted per turn and surfaced on the node, in chat,
and in export XMP.

---

### G7. Cost preview exists but is not a gate; caps are unreachable  *(M-3.3)* — **MAJOR** (was a blocker)

*Why it still matters:* `/api/quote` and the pre-flight `assert_budget` closed the serious hole —
the mid-run abort that charged for an orphan artifact is gone, and `402` is a proper status. What
remains: **Weave** fires without anyone having seen a number (`web/app.js:327-348` does not call
`/quote`), so the cross-flow invariant "cost before commit" (`UX_FLOWS.md:90`) is still violated by
default; there is no refund/rollback concept; and when a user hits "thread budget $2.00 exceeded"
their only remedy is to set an environment variable and restart (`usage.py:15-16`, read at import).
That is a dead end for a non-developer.

*Smallest fix:* auto-quote on prompt change and render it in the pre-flight row; require the number to
be on screen before **Weave** enables; make both caps editable in Settings and persisted, not env-only.

*Research-complete fix:* `08-security-quota/usage.py` — strict unknown-model handling, key-shaped
string scrubbing, append-only enforcement, projection-before-call — already tested
(`10-eval/ACCEPTANCE_CHECKLIST.md` §4).

---

### G8. Plan card and Pick are half-built  *(M-2.1, M-3.4)* — **MAJOR**

*Why it matters:* these are the two named differentiators — an **editable** plan (vs Lovart's
read-only chain) and the Say/**Pick**/Polish grammar. Both now render something and neither is
interactive: the plan is an `<ol>` you cannot touch (`web/app.js:98-116`), and 4-up variants are
auto-pinned to the board with no rationale, no cycling, and no keep/discard
(`conductor.py:190-201`). Shipping here means shipping the *appearance* of the differentiators.

*Smallest fix:* split `/run` into `POST /threads/{id}/plan` (returns a plan, commits nothing) and
`POST /threads/{id}/run {plan}` (executes the possibly-edited plan); make the step list
delete + drag-reorder. For Pick: hold the 4 variants in a grid instead of pinning them, add
`Tab`/arrow focus and `Enter` to keep, and store unkept ones as `parent_id` children — the lineage
column already exists, so the variant stack is nearly free.

*Research-complete fix:* `05-conductor/PROTOCOL.md` §2 `conductor-plan/1` — typed, validated,
topologically ordered step graph with `parse_plan` / `order_steps` / `parse_critique`
(`05-conductor/conductor.py:378, 534, 492`), already covered by 58 tests, plus per-step SSE so the
plan card fills in live (the `?stream=1` transport already exists at `server.py:153-163`).

---

### G9. Undo covers one action; moves and deletes are unrecoverable  *(M-4.4)* — **MAJOR**

*Why it matters:* `undo_log` and `POST /projects/{id}/undo` exist, but `Memory.undo` only reverses
`add_node`. A drag is still a destructive `UPDATE` (`store.py` `update_node`), `delete_node` is not
logged, and there is no project snapshot. The acceptance bar is ≥50 node-scoped steps plus a
per-turn snapshot with ≤5 s restore.

*Smallest fix:* log `update_node` (old geometry) and `delete_node` (full row) into `undo_log`, and
have `undo` dispatch on all three actions; cap the log per project; add a per-turn snapshot row (a
JSON dump of the node list is sufficient at this scale) with a "restore this turn" affordance in chat.
Also expose the existing `DELETE /api/nodes/{id}` in the UI — the endpoint works and `web/app.js`
never calls it (verified: 0 occurrences).

*Research-complete fix:* the append-only Memory — `trg_messages_no_update/no_delete`,
`trg_artifacts_frozen`, `trg_usage_no_update/no_delete` (`04-helix-arch/schema.sql:79-95, 194,
348-360`), board-as-projection so unpinning never destroys matter, `v_board_scene` as the read model
(`:375`), and `POST /projects/{id}/snapshot` (`openapi.yaml:149`).

---

### G10. Uploads land on the board but never reach a generation  *(M-5.4, P2-4c)* — **MAJOR**

*Why it matters:* upload now works end-to-end (base64 JSON, ≤5 MB, drag-drop, pinned node) but the
bytes are inert. `Spoke.image()` has no image-input parameter (`spokes/base.py:40`), so a logo or a
reference photo cannot condition anything. This blocks logo compliance, character consistency
(P2-4c), image-to-video, and the "attach references to one turn" flow (`FEATURE_MATRIX.md:88`).

*Smallest fix:* add an optional `reference_images` argument to the `image()` contract and pass it
through on the Gemini path first — `generateContent` already accepts inline image parts, which is the
same shape the spoke reads on the way out (`spokes/gemini_spoke.py:79-92`).

*Research-complete fix:* Shelf with workspace promotion, `@` mention resolution, and the
`brand_assets` binding from `04-helix-arch/schema.sql:304`.

---

### G11. Ledger is collected but not shown  *(M-6.4)* — **MAJOR**

*Smallest fix:* a Spend panel — the events table grouped by turn with engine, action, units, USD, plus
today-vs-cap; add `message_id` to `usage_events` so per-turn attribution is exact rather than
per-thread.

*Research-complete fix:* `v_usage_daily` (`schema.sql:363`) and `/usage/summary`
(`openapi.yaml:996`).

---

### G12. Video, audio, 3D, Fanout, Sweep, PSD  *(M-3.5 + all of P2)* — **deferred, deliberately**

The project's own strategy note ships fewer modalities in exchange for image-loop reliability
(`FEATURE_MATRIX.md:134`), and I agree. **I would consciously re-tier M-3.5 (video) to P2** for the
first usable release: it is the largest new subsystem (async job polling, long-running state, MP4
handling) and it cannot make the image loop usable. If it must stay in MVP, wire
`07-loom/loom.py`'s `DemoVideo` (`:928`) and `VeoVideo` (`:1007`) behind a `video` node type with a
job-polling endpoint; `PIPELINES.md` §Pipeline 4 specifies the backends and the stub-first policy, and
`06-board-ui/UI_SPEC.md` §4.3 specifies the placeholder node.

---

## 6. Defects still open at `1bfa56d`

Small, user-visible, no design decision required.

| # | Defect | Location | Impact |
|---|---|---|---|
| 6.1 | No packaging; `python3 -m atelier` only works from the package parent; failure is `No module named atelier` | repo has no `pyproject.toml` | first-run failure for the target user |
| 6.2 | `POST /api/nodes/{missing}` returns **no HTTP response** (`HTTP 000`); `TypeError` in `store.get_node` | `server.py:419-422` has no `try`; `get_node` does `dict(...fetchone())` | any stale node id — e.g. a second tab after an undo — drops the connection |
| 6.3 | Refine target chosen by regex + last-rendered node | `web/app.js:309-311` | the edit feature is undiscoverable and aims at the wrong node |
| 6.4 | `palette` / `title` silently ignored by both paid image spokes | `spokes/openai_spoke.py:70-85`, `spokes/gemini_spoke.py:79-92` | brand kit works in demo, does nothing when you pay |
| 6.5 | `undo` reverses only `add_node` | `store.py` `undo` | moves and deletes are unrecoverable |
| 6.6 | `DELETE /api/nodes/{id}` is unreachable from the UI | `web/app.js` (0 matches) | board can only grow |
| 6.7 | Provider / model / mode controls are **illegible** — light `color: inherit` on the browser-default white `<select>`, because the background rule only covers `.field select` and these three live in `.row` | `web/styles.css:52-56` vs `web/index.html:56-70` | the exact controls needed to switch from demo to a paid key cannot be read (visible in `/tmp/atelier-opus/live-ui.png`) |
| 6.8 | Malformed brand-kit JSON throws uncaught; the click looks successful | `web/app.js:298` | silent data loss |
| 6.9 | Manual `model` override ignored for images | `conductor.py:263` | `dall-e-3` silently becomes `gpt-image-1` |
| 6.10 | No `GET /api/providers`; model is a free-text box | `server.py`, `web/index.html:62` | typos become silent fallbacks |
| 6.11 | No fit-to-content / zoom reset; `camReadout` is a passive `<span>` | `web/app.js:170-197` | once you pan away, finding your work is manual |
| 6.12 | `ATELIER_HOST=0.0.0.0` bypasses the `Host` guard entirely — unauthenticated `POST /api/keys` and `POST /run` on the LAN | `server.py:107-115` | secret write + spend by anyone on the network; refuse non-loopback binds without a token |
| 6.13 | Budget caps are import-time env constants | `usage.py:15-16` | hitting a cap is a dead end without an env var + restart |
| 6.14 | `refreshBoard` rebuilds all node DOM and re-requests every image on every turn and every project boot | `web/app.js:118-144` | the M-1.2 200-node bar is unreachable by construction |
| 6.15 | `TOP100 catalog` is a `window.alert()` | `web/app.js:371-375` | a debug affordance in the primary UI |

---

## 7. Ranked ship list — top 15

Ranked by **(unblocks 成品可用) ÷ (work)**. Items **1–7** are the minimum that lets a non-developer
complete **install → keys → brief → generate → edit → export** once, end to end. None of 1–7 needs a
new dependency or a new model vendor.

| # | Ship item | Fixes | Sev | Why now |
|---|---|---|---|---|
| **0** | Resolve the credits-vs-BYOK spec conflict; fork `ACCEPTANCE-BYOK.md` | §2 | blocker | Costs a document. Without it "done" is undefined and M-6 is unscoreable |
| **1** | **Designer export**: PNG-canonical artifacts (adopt `07-loom/loom.py:318`), `/export?fmt=png\|jpeg\|pdf&scale=`, stdlib one-page PDF, per-node Export button, rights line | M-6.1, M-6.3, G1 | blocker | The loop still has no exit. Highest value per line of code in the repo |
| **2** | **Selection model + Refine button**: click-to-select, visible ring, `parent_artifact_id` from the selection, target confirmation chip; delete the magic-word regex | M-4.1, M-2.6, 6.3, 6.6 | blocker | The edit backend already works — this is the UI that makes it reachable and correctly targeted |
| **3** | **Brand kit → paid pixels**: deterministic kit suffix on every image prompt for every provider; multimodal critic that sees the image; catch the kit `JSON.parse` | M-5.3, M-5.1, 6.4, 6.8 | blocker | A feature that works only when it's free is worse than one that's absent |
| **4** | **Context ledger**: last-N turns + board inventory into the planner; `selected_node_id`; `target_node` in the plan schema | M-1.4, M-2.6 | blocker | Item 2 has nothing to refine against without it; every turn is a cold start |
| **5** | **Installable**: `pyproject.toml` + `atelier` console script, browser auto-open, port fallback, first-run key empty state, honest `atelier.html` copy | M-1.1, 6.1 | blocker | The target user cannot start the product today |
| **6** | **Make the quote a gate**: auto-quote on prompt change, cost on screen before **Weave** enables, caps editable in Settings | M-3.3, 6.13 | blocker | `/api/quote` exists but nothing forces it — "cost before commit" is still violated by default |
| **7** | **Shipped-surface polish**: legible selects, `try` around every handler, `GET /api/providers`, fit-to-content + zoom reset, diff-render the board, drop the `alert()` | 6.2, 6.7, 6.10, 6.11, 6.14, 6.15 | blocker (aggregate) | A dozen one-to-five-line fixes on the controls a first-time user touches first |
| **8** | **Provenance surfaced**: join artifacts into `/board`, engine chip per node, report the image model (not the planner model) in chat | M-3.2, G6 | major | Fail-closed made it honest; it is still invisible, and it is the core BYOK report |
| **9** | **Pick grid**: hold variants instead of auto-pinning, per-variant rationale, `Tab`/`Enter`, unkept → `parent_id` children | M-3.4 | major | 1/3 of the Say/Pick/Polish grammar; the lineage column already exists |
| **10** | **Editable plan + `/plan` split**: delete and reorder steps, execute the edited plan | M-2.1 | major | The headline differentiator vs Lovart's read-only chain |
| **11** | **Undo for everything**: log moves and deletes, dispatch on action, per-turn snapshot + restore | M-4.4, 6.5 | major | No design tool ships without undo; today only "add node" is reversible |
| **12** | **References into generations**: `reference_images` on the `image()` contract, Gemini inline parts first | M-5.4, P2-4c | major | Uploads currently land on the board and are inert |
| **13** | **Spend panel**: per-turn ledger table, `message_id` on usage rows | M-6.4 | major | The BYOK trust story, and the data is already collected |
| **14** | **Auth or refuse**: reject non-loopback binds without a token; kill the `0.0.0.0` hole | P2-5b, 6.12 | major | One conditional stands between a local studio and a LAN-writable secret store |
| **15** | **Clarifying questions** (`ask` step kind, ≤3, grouped, "use defaults") + **latency instrumentation** (timestamps on phase events) | M-2.3, M-2.2, M-2.4 | major | Three acceptance criteria are currently *unmeasurable*, so they can never be signed off |

**Explicitly deferred / re-tiered:** M-3.5 video → P2 (largest new subsystem; cannot make the image
loop usable). M-6.2 free-tier watermark → out of scope under BYOK. M-4.3 background removal → after
item 2 (same segmentation dependency). All P2 items stay P2 except P2-5b's auth half, pulled forward
to item 14.

**Ship gate:** `10-eval/ACCEPTANCE_CHECKLIST.md` §5 and §7 still record the same two open items —
"real end-to-end runner" and "board UI renders `v_board_scene`". Items 1–8 above are precisely that
integration. The live gate is now 32 tests (`atelier.tests.test_helix` + `test_evolve`) against a
research harness of 58 (`10-eval/test_helix.py`); every item above should land with its research test
bound, or this scorecard regresses silently.

---

## 8. What is already solid (do not rewrite these)

- **The BYOK boundary is genuinely well built, and got better.** `assert_official_host`
  (`spokes/base.py:44-49`) is now enforced at **save** time too (`400 unofficial_host`, verified);
  keyring writes are atomic with `fchmod 0600` and refuse symlinks; keys are never returned
  (`keyring.public_status`); web file serving is path-contained via `safe_under` (`helix/paths.py`);
  image downloads refuse non-HTTPS and refuse redirects (`spokes/openai_spoke.py:88-99`).
- **Fail-closed is the right call and was implemented correctly.** A paid provider that fails no
  longer mints a demo SVG dressed as a success (`conductor.py:272-284`), and a missing key surfaces as
  `422 auth` (verified). This removed the worst trust bug in the product.
- **Pre-flight quoting is real.** `helix/quote.py` prices tokens *and* images from a dated table,
  distinguishes **priced** from **conservative** estimates (`usage.is_priced` — unknown ≠ free), and
  refuses before spending. That is a better cost model than most hosted products expose.
- **Demo mode remains the right product decision** — a zero-key run still puts something on the
  board, so the studio is never a blank screen. It needs *labelling* and PNG output, not removal.
- **Memory is a clean small store** with sane concurrency now (`RLock`, WAL, `busy_timeout`,
  additive `_migrate()`), and `artifacts.parent_id` + `undo_log` are exactly the right primitives for
  variant stacks and undo. The research schema is a superset, not a contradiction.
- **The research pack is unusually complete.** For nearly every gap above, the fix already exists —
  specified, and often tested — under `research/fable5/`. This remains a **wiring** backlog, not a
  design backlog, which is the good kind of debt.

---

### Appendix — reproduction

```bash
# nothing under /workspace is written
export ATELIER_HOME=/tmp/atelier-opus/home3 ATELIER_RUNTIME=/tmp/atelier-opus/rt4 ATELIER_PORT=8792
cd /workspace && python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve   # 32 OK
cd /workspace && python3 -m atelier &

B=http://127.0.0.1:8792
PID=$(curl -s $B/api/projects | python3 -c "import sys,json;print(json.load(sys.stdin)['projects'][0]['id'])")
TID=$(curl -s $B/api/projects/$PID/threads | python3 -c "import sys,json;print(json.load(sys.stdin)['threads'][0]['id'])")

# fail-closed (fixed):        422 {"code":"auth"}
curl -s -X POST $B/api/threads/$TID/run -H 'Content-Type: application/json' \
  -d '{"prompt":"logo","mode":"fast","provider":"openai"}'

# host lock at save (fixed):  400 {"code":"unofficial_host"}
curl -s -X POST $B/api/keys -H 'Content-Type: application/json' \
  -d '{"provider":"openai","key":"sk-x","base_url":"https://evil.example.com"}'

# cost preview (new):         estimated_usd / priced / breakdown
curl -s -X POST $B/api/quote -H 'Content-Type: application/json' \
  -d '{"provider":"openai","prompt":"poster","count":4}'

# export is archival, not a deliverable:
curl -s -o /tmp/p.zip "$B/api/projects/$PID/export" && python3 -c "import zipfile;print(zipfile.ZipFile('/tmp/p.zip').namelist())"
# -> project.json, board.json, threads.json, artifacts/*.svg, artifacts.json   (no PNG, no PDF)

# still crashes (open):       HTTP 000
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST $B/api/nodes/nope \
  -H 'Content-Type: application/json' -d '{"x":5}'
```
