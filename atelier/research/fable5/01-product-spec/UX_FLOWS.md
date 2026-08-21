# UX_FLOWS.md — Atelier core flows (informed by Lovart public teardown)

Flows are written for Atelier. Where a step mirrors or deliberately diverges from Lovart's publicly
documented behavior, the Lovart reference is cited inline. Source URLs are listed in
`FEATURE_MATRIX.md` §1 and referenced here by the same S-numbers.

Layout baseline (matches Lovart's public tutorial description, S22): chat panel left, infinite canvas
center, toolbar top (engine picker, export, undo/redo, settings). Prompt box docked bottom-center of
the chat panel with mode toggle (Plan/Direct), `@` mention, and attach buttons.

---

## Flow 1 — New project

Benchmark: Lovart's reviewer measured sign-up → first generation in under 3 minutes with no credit
card and no onboarding wizard (S20). Atelier target: **≤ 2 minutes, ≤ 3 required decisions.**

1. `Home → New Project`. Modal with exactly three fields:
   - Name (prefilled "Untitled project — {date}").
   - StyleLock kit selector: `None / existing kit / create new` (Lovart equivalent: Brand Kit selector, upper-left of canvas, S12). Default **None** — kit is never required.
   - Starting mode: `Plan` (default) or `Direct` (Lovart: Thinking vs Fast, S3).
2. Project opens on an empty Boardroom canvas. Chat shows one system message: "Describe what you want to make. Attach references with the clip icon or `@` to mention a kit or shelf asset." No tour, no wizard.
3. Empty-state prompt box shows 3 example briefs (poster / social pack / product shot) as one-click chips.
4. A **Thread** is created implicitly with the first message. Additional threads: `+` in the chat header; each thread binds to the whole board or to a selected frame.

Edge cases:
- No verified email → generation blocked, canvas exploration allowed; inline banner with resend link.
- Zero credits → prompt box stays active but the Generate button shows cost and a top-up link instead of firing (Lovart shows all credit costs before generation, S11).

## Flow 2 — Chat (agent conversation)

1. User types a brief. Optional: attach files (per-turn references, S12), `@`-mention a StyleLock kit or Shelf asset (S12), toggle Plan/Direct via the switch in the prompt box (Lovart uses a lightbulb icon in the input box for Thinking Mode, S3).
2. **Plan mode:**
   a. Helix returns a visible plan card: numbered steps (analyze → clarify → concepts → generate → assemble). Diverges from Lovart: steps are editable — the user can delete or reorder steps before running (Lovart displays a task chain but public docs do not describe editing it, S21).
   b. If the brief is underspecified, Helix asks ≤3 clarifying questions in a single grouped card (Lovart's agent asks ~3 questions, S4). Every question has a "use defaults" skip.
   c. User hits **Run plan**. Progress renders per-step on the plan card; generated nodes appear on the canvas as they complete, each tagged with the engine name (Lovart displays the model name above each result, S21).
3. **Direct mode:** prompt → Router → single generation. No plan card, no questions. Target latency: first pixels < 15 s.
4. Every chat message that produced assets shows chips linking to those canvas nodes; clicking a chip pans/zooms to the node. Conversely, selecting a node filters chat to messages that touched it.
5. Referring expressions ("the logo", "that headline") resolve via the context ledger to node IDs; the resolved target is shown as a small confirmation chip on the user's own message ("→ Logo v3") so misresolution is visible before the edit lands.

## Flow 3 — Generate

1. Prompt submitted (either mode). Pre-flight row appears under the prompt: **engine (auto-picked, overridable dropdown), variant count (default 4 in Plan / 1 in Direct), size preset, credit cost**. Nothing fires until cost is visible (Lovart: costs displayed before generation, S11).
2. Generation runs; skeleton frames appear on the canvas at final size so layout doesn't shift.
3. Plan mode returns a **Pick grid**: variants side-by-side, each with a one-line rationale (Lovart's concept options carry explanations, S4). Interactions:
   - `Tab` / arrow keys cycle focus; `Enter` keeps the focused variant; `K` keeps-and-continues (keeps variant, asks Helix for 4 more in that direction).
   - Non-kept variants collapse into the node's variant stack (recoverable, never deleted).
4. Kept node lands on the canvas with a provenance chip: engine, seed, prompt hash, kit applied.
5. Failure path: engine error → the variant slot shows retry (same engine) and reroute (Router picks next-best engine) buttons; credits for failed slots auto-refund.

## Flow 4 — Refine

Anchored on the publicly documented Touch Edit loop: click a region, describe the change, only that
region re-renders (S6, S18, S20 — reviewer-reported ~80% mask reliability).

1. **Spot Edit (click):** click any object on a node → auto-mask overlays with a marching-ants preview. If the mask is wrong (the ~20% case), press `B` for the manual brush. Type the instruction ("change to soft mint green gradient", S20's own example) → only the masked region re-renders. Composition outside the mask is byte-identical.
2. **Text edit:** click a text layer → caret editing in place, real vector text; font/size/color from the StyleLock kit are offered first (Lovart: text as an editable layer, retype without touching layout, S20).
3. **Chat refine:** with a node selected, plain-language instructions apply to it ("make it more minimalist", S18). Without a selection, the ledger resolves the target and shows the confirmation chip (Flow 2.5).
4. **Sweep (P2):** select node → Sweep → choose one variable (palette / font pairing / background) → N-way strip renders for side-by-side pick (Lovart "Tab" quick-edit reading, FEATURE_MATRIX §3.2).
5. Every refine writes to the node's variant stack; `Cmd/Ctrl+Z` is node-scoped, project snapshots are turn-scoped.

## Flow 5 — Export

1. Select node(s) → `Export` (toolbar) or `E`. Dialog shows:
   - Format: PNG / JPEG / SVG (vector-text nodes) / PDF-RGB / MP4 for video nodes. (Lovart advertises PNG, JPEG, SVG, PDF CMYK+bleed, PSD — S1, S7; its layered-PSD claim is contested by S20, so Atelier ships layered PSD only when it can pass the acceptance test in ACCEPTANCE.md §P2-3.)
   - Size/scale (1x/2x/4x), background (transparent for PNG).
   - License line for the current plan (paid = full commercial rights, matching Lovart's public policy, S9).
2. Free plan: export proceeds with a corner watermark + upgrade link (Lovart free exports are watermarked, S20).
3. **Fanout (P2):** choose a platform pack (IG Feed/Story/Reel, X, LinkedIn, Pinterest...) → one job emits all sizes, zipped, named `{project}-{platform}-{WxH}.{ext}` (Lovart batch-exports 20+ platform variants at once, S20).
4. Export metadata: every file embeds XMP with engine name, prompt hash, and Atelier project URL — extends the provenance Lovart shows in-app (S21) into the artifact itself.

## Flow 6 — Key settings

| Setting | Location | Behavior | Lovart reference |
|---|---|---|---|
| StyleLock kit (project default) | Canvas upper-left selector | Every generation in the project references the kit; per-prompt `@` mention overrides for one turn | Identical scoping to Brand Kit per official docs (S12) |
| Kit management | Workspace → Kits | CRUD kits: logos, palette w/ roles, fonts, tone notes; one kit per brand | S7, S12 |
| Shelf (assets) | Prompt-box shelf icon | Upload/reuse assets across projects; `@` mention attaches to a turn | Assets Library (S12) |
| Mode default | Prompt box toggle + Settings → Defaults | Plan or Direct as project default; per-turn override always available | Thinking/Fast switchable at any point (S3) |
| Engine routing | Settings → Engines | Auto (Router) default; per-engine disable; manual pick lives in the pre-flight row, not buried in settings | Auto-routing + manual model list (S8, S18) |
| Variant count | Pre-flight row | 1–8, remembered per project | "dozens of variants" claim scoped down for cost sanity (S1) |
| Credits & plan | Settings → Billing | Live balance, per-turn history with engine + cost, top-up | Credit dashboard with pre-generation costs (S11) |
| Sessions/devices | Settings → Security | Session list + revoke; no hard device cap at MVP | Lovart caps at 2 desktop + 1 mobile (S11) — Atelier defers caps until abuse data exists |
| Clarifying-question budget | Settings → Agent | 0–3 questions before Helix proceeds with defaults | Lovart's ~3-question behavior (S4), made user-controllable |

---

## Cross-flow invariants

1. **Cost before commit** — no action consumes credits without the cost having been on screen (S11 parity).
2. **Nothing destructive** — variants collapse, never delete; every agent turn snapshots the project.
3. **Provenance everywhere** — engine chip on node, in chat, in export metadata (extends S21).
4. **Selection is the context** — chat instructions always target the selection first; resolver only guesses when nothing is selected, and shows its guess.
5. **Mode toggle is always one click** — matching Lovart's any-time Thinking/Fast switch (S3).
