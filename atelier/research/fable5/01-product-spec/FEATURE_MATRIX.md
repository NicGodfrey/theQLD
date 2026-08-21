# FEATURE_MATRIX.md — Lovart AI (public teardown) vs Atelier (proposed, "Helix" architecture)

Method: public marketing pages, official docs, official blog, and third-party reviews only. No private APIs,
no authenticated scraping. Every Lovart claim below carries a public URL. Where public sources disagree,
the discrepancy is flagged rather than resolved.

Naming used throughout:
- **Lovart** — the shipping product at lovart.ai.
- **Atelier** — the proposed original product (this project).
- **Helix** — Atelier's agent/orchestration architecture (planner + router + editor loop), the counterpart to Lovart's MCoT.

---

## 1. Source index

| # | Source | Type | URL |
|---|--------|------|-----|
| S1 | AI Design Agent feature page | Official | https://www.lovart.ai/features/ai-design-agent |
| S2 | MCoT Engine feature page | Official | https://www.lovart.ai/features/mcot-engine |
| S3 | "Inside the MCoT Engine" | Official blog | https://www.lovart.ai/blog/inside-mcot-engine-ai-design-reasoning |
| S4 | "MCoT vs Prompt Engineering" | Official blog | https://www.lovart.ai/blog/mcot-vs-prompt-engineering-experiment |
| S5 | "What Is an AI Design Agent?" | Official blog | https://www.lovart.ai/blog/ai-powered-design-agent-for-creators |
| S6 | Touch Edit feature page | Official | https://www.lovart.ai/features/touch-edit-ai |
| S7 | AI Brand Tool feature page | Official | https://www.lovart.ai/features/ai-brand-tool |
| S8 | All-in-one models feature page | Official | https://www.lovart.ai/features/all-in-one-ai-models |
| S9 | AI video generator tools page | Official | https://www.lovart.ai/features/ai-video-generator-tools |
| S10 | AI video generator for ads page | Official | https://www.lovart.ai/features/ai-video-generator-for-ads |
| S11 | Pricing page + credits FAQ | Official | https://www.lovart.ai/pricing |
| S12 | Docs: Adding References (Assets Library, Brand Kit, @-mentions) | Official docs | https://www.lovart.ai/docs/how-to-prompt/adding-references |
| S13 | "AI Animated Videos from Scripts" (TTS/BGM/SFX, 50 free designs/mo) | Official blog | https://www.lovart.ai/blog/ai-animation-from-script |
| S14 | AI Music Generator guide | Official blog | https://www.lovart.ai/blog/ai-music-generator-complete-guide-2026 |
| S15 | Brochure with Brand Kit (Talk·Tab·Tune) | Official (insight subdomain) | https://insight.lovart.ai/blog/how-to-create-brochure-with-brand-kit |
| S16 | UI layouts with Brand Kit (Talk·Tab·Tune) | Official (insight subdomain) | https://insight.lovart.ai/blog/how-to-create-ui-layouts-with-a-brand-kit |
| S17 | lovart-skill (OpenAPI agent skill; projects/threads; image/video/audio/3D) | Official GitHub | https://github.com/lovartai/lovart-skill |
| S18 | Framia review | Third party | https://framia.converge.ai/blog/lovart-ai-review |
| S19 | PixAI review | Third party | https://blog.pixai.art/en/lovart-ai-review-2026-what-it-does-well-where-it-falls-short-and-alternatives/ |
| S20 | ReviewNexa 30-day test | Third party | https://reviewnexa.com/lovart-review/ |
| S21 | FlipHTML5 review (Talk/Tab/Tune modes, model roster) | Third party | https://fliphtml5.com/blog/lovart-ai-review-how-the-worlds-first-design-agent-ignites-your-creativity-with-seamless-precision/ |
| S22 | lovart.fyi tutorial (UI layout: chat left, canvas center, toolbar top) | Third party | https://lovart.fyi/blog/lovart-tutorial |
| S23 | lovart.fyi video models guide | Third party | https://lovart.fyi/blog/lovart-video-models-guide |

Caution: `lovart.me` and `lovart.fyi` are not the official domain; they are used here only for UI-layout and
model-comparison observations that are consistent with official pages, never as sole evidence for a feature.

---

## 2. Feature matrix

Legend for the Atelier column: **MVP** = in first shippable release; **P2** = post-MVP parity; **Skip** = deliberately not built.

### 2.1 Workspace / canvas

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Infinite spatial canvas | "ChatCanvas" — infinite, zoomable workspace where all assets (images, video, campaign shots) coexist; the session is treated like a project file, not a prompt feed (S1, S3). | **Boardroom**: infinite pan/zoom canvas, CRDT-backed document so multiplayer comes later without a rewrite. Assets are nodes with position, z-order, and provenance (which prompt/model produced them). | MVP |
| Chat docked to canvas | Chat panel on the left, canvas center, toolbar top with model selector and export (S22); "one prompt → results on canvas" (S1). | Same tripartite layout. Chat messages carry structured "actions" (generated node IDs) so clicking a message highlights its outputs on the canvas. | MVP |
| Multi-asset context ("treat session as project file") | MCoT "maintains context across your entire project, remembering brand guidelines, previous decisions and iteration history" (S2); "Move the logo from Image A to Image B" style commands (S3-adjacent architecture doc). | Helix keeps a per-project **context ledger**: brief, style constraints, accepted/rejected variants, named entities ("the logo", "hero shot"). Chat resolver maps referring expressions to canvas node IDs. | MVP (ledger), P2 (cross-asset transfer edits) |
| Editable layers on canvas | Text is an editable layer — click headline, retype, layout preserved (S20); "projects organized with editable layers" (S19). | Generated assets decompose into layers where the pipeline supports it (text layers always; image layers P2 via segmentation). Text rendered as real vector text, not pixels, whenever the generator returns layout metadata. | MVP (text layers), P2 (full layer decomposition) |
| Version history on canvas | "ChatCanvas history" vs "files in chat threads" (S6 comparison table). | Every node keeps a variant stack (linear undo per node + project-level snapshot on each agent turn). | MVP |

### 2.2 Agent reasoning

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Deliberate planning mode | **Thinking Mode**: MCoT pauses 5–15 s; analyzes business context, audience, brand; decomposes vague briefs into structured plans (audience modeling, asset planning, visual strategy, model orchestration) (S2, S3). Toggled via lightbulb icon in the input box (S3 synthesis). | **Helix Plan mode**: LLM planner emits a typed plan graph (analyze → ask → concept → generate → assemble). Plan is *visible and editable* before execution — differentiator: Lovart shows reasoning, Atelier lets you edit the plan steps. | MVP |
| Fast/direct mode | **Fast Mode** skips the MCoT chain, generates immediately; for moodboards and brainstorming; switchable mid-project (S3). | **Helix Direct mode**: prompt → router → generator, no planning pass. Same toggle position (input box). | MVP |
| Clarifying questions | Agent asks ~3 clarifying questions before generating when brief is underspecified (S4). | Planner asks at most N (configurable, default 3) blocking questions; each has a "skip, use defaults" escape so the agent never stalls. | MVP |
| Parallel constraint chains | Marketing describes parallel chains for color, composition, typography, brand compliance, storytelling that cross-reference each other (S5). Note: S4/S8 expand MCoT as "Mind Chain of Thought", S5 as "Multi-Chain of Thought" — official copy is inconsistent. | Helix runs a post-generation **critic pass** (single model, rubric with color/type/layout/brand checks) instead of claiming parallel chains. Cheaper, honest, measurable. | MVP (critic), P2 (specialist critics) |
| Explained outputs | Concept options come "each accompanied by a short explanation of why the composition works" (S4). | Each variant carries a one-sentence rationale generated in the same planner call (zero extra cost). | MVP |
| Web research pre-generation | "Use Web Search and Thinking Mode to analyze product materials, competitor video ads and platform specs" (S10). | Helix tool: web search for reference/spec lookup during Plan mode. | P2 |

### 2.3 Editing

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Local region edit | **Touch Edit**: click a region, change only typography/objects/colors/small layout, no full regeneration (S1, S6). Click-to-select recognizes object boundaries without manual masking (S18). Reported ~80% reliability by an independent 30-day test (S20). | **Spot Edit**: click → auto-mask (segmentation model) → inpaint with instruction. Manual mask brush as fallback for the ~20% failure case Lovart's reviewers report. | MVP |
| Region / element tools | Distinct tools: Region Editing, Edit Elements, Touch Edit (S19, S3). | One tool with three entry points (click object, marquee region, pick layer) rather than three named tools — fewer concepts to learn. | MVP |
| Conversational refinement | Follow-up prompts like "make the logo more minimalist", "darker, like espresso" resolve against the selected asset (S18, S22). | Chat edits apply to current selection; without selection, resolver uses the context ledger (last-touched node). | MVP |
| Background removal, outpaint/canvas extension | Background removal and canvas extension called out as iteration keepers (S20); outpainting on canvas (S8). | Both as canvas verbs (right-click or chat). | MVP (bg removal), P2 (outpaint) |
| A/B variable cycling | One reading of "Tab": quick-edit menu to cycle 5 background colors / 3 font pairings without regenerating the subject (S15-adjacent; sources disagree — see §3). | **Sweep**: select a node, pick one variable (palette / font / layout), generate an N-way strip. | P2 |

### 2.4 Brand & assets

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Brand Kit | Upload once (logos, colors, fonts, guidelines); auto-applies to every generation (S1, S7). Apply per-generation via `@` mention or per-project via selector in canvas upper-left; multiple kits, one per brand (S12). | **StyleLock**: same two application scopes (per-project default + per-prompt `@` override). Kit = logos (SVG/PNG), palette (hex + roles), type (font files or Google Fonts refs), tone notes. Kit is injected into Helix as hard constraints checked by the critic pass. | MVP |
| Assets Library | Stores character/audio/video assets, reusable across projects, attached to prompts via `@` mention; preloaded library + user uploads (S12). | **Shelf**: project-scoped by default, promotable to workspace scope. Same `@` mention UX. Characters P2 (needs identity-consistency support in generators). | MVP (upload/reuse), P2 (characters) |
| Reference files per conversation | "Upload Files: attach references to a one-off conversation instead of saving them for reuse" (S12). | Drag-onto-chat attaches to that turn only. | MVP |

### 2.5 Modalities & models

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Image generation | Multiple engines: Nano Banana Pro (proprietary branding), Flux 1.1, Seedream 4.5 (text rendering), plus GPT-Image, Ideogram cited in reviews (S8, S19, S21). | 2 engines at MVP: one aesthetic-priority, one text-rendering-priority (exact vendors decided by eval, not marketing). Adapter interface so adding engines is config, not code. | MVP |
| Video generation | Sora 2, Veo 3.1, Kling 2.6, Hailuo 2.3, Wan 2.6, Seedance 2.0; keyframes, camera/motion params, vertical/square/landscape cuts, 4K upscaler (S9, S10, S23). | 1 video engine at MVP (image-to-video + text-to-video, ≤10 s, 1080p). Keyframes/camera control P2; upscaler P2. | MVP (basic), P2 (multi-engine, control, 4K) |
| Audio generation | BGM, songs, SFX (S17); TTS voiceover, background music, sound effects in animation workflow (S13); Suno integration cited (S21). | P2: music beds + SFX via one licensed engine; TTS P2. Audio nodes live on the canvas timeline-less at first (attached to video nodes). | P2 |
| 3D generation | 3D models from text or images; Tripo integration (S17, S21); `.blend` export claim in review (S21). | P2/Skip for MVP: text-to-3D preview node with GLB export. No editing. | P2 |
| Model picker (auto + manual) | MCoT auto-routes prompt to best model (S8); users can also choose the model from a list before generating (S18, S22); the active model name is displayed above each generated result (S21). | **Router**: default = auto (Helix router chooses engine, logs why). Manual override dropdown per prompt. Provenance chip on every node showing engine + settings — same transparency Lovart shows. | MVP |

### 2.6 Interaction grammar

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Talk / Tab / Tune | Official three-stage loop: **Talk** = natural-language intent; **Tab** = agent presents multiple layout/option branches to pick from; **Tune** = surgical, conversational micro-adjustments on canvas (S15, S16, S21). Third-party sources disagree on whether "Tab" is the keyboard key or an options gallery (see §3). | **Say / Pick / Polish** (renamed, same grammar): Say = prompt; Pick = variant grid (always ≥3 options in Plan mode); Polish = Spot Edit + chat refinement. Keyboard: `Tab` cycles variants in the Pick grid — adopting the strongest reading of Lovart's pattern. | MVP |
| Multi-variant generation | "One prompt generates dozens of Design Agent variants" (S1); 8 concept options in the MCoT experiment (S4). | Pick grid defaults to 4 variants in Plan mode, 1 in Direct mode (cost control), user-adjustable 1–8. | MVP |

### 2.7 Projects, export, plans

| Capability | Lovart (public evidence) | Atelier / Helix proposal | Tier |
|---|---|---|---|
| Projects & threads | No project limits; credit pool is the constraint (S20). Official OpenAPI skill exposes project & thread management: list/add/switch/rename/remove projects, threads under projects, local state persistence (S17). | Workspace → Projects → Threads (a thread = one agent conversation bound to one canvas region or the whole board). Public API parity P2. | MVP (projects+threads), P2 (API) |
| Export formats — images | PNG, JPEG, SVG, PDF (CMYK + bleed), PSD (S1, S7). But an independent test states exports are flattened and layer structure is lost (S20) — official PSD claim vs review contradiction flagged. | MVP: PNG, JPEG, SVG (for vector/text nodes), PDF (RGB). P2: PSD **with real layers** (text + image layers preserved) and CMYK+bleed PDF — turning Lovart's contested claim into a checkable differentiator. | MVP / P2 as listed |
| Export — video/audio | MP4 export confirmed (S20); native-audio video models (S23). | MP4 (H.264) at MVP; WebM + audio stems P2. | MVP |
| Batch platform variants | Master design resized to Instagram Feed/Stories/Reels, Facebook, LinkedIn, X, Pinterest; batch export of 20+ variants at once (S20). | **Fanout**: preset size packs per platform, one export job. | P2 |
| Credits & modes | Credit-based; cost varies by model/size/quality; shown before generation. Fast Generation (credits) vs Unlimited Relax Generation (free slow queue on designated models, tiered priority). Monthly credits don't roll over; top-ups last 366 days. Team plan; 2 desktop + 1 mobile sessions per account (S11). | Credits with pre-generation cost preview (MVP). Relax queue Skip at MVP (needs owned GPU capacity). Rollover top-ups P2. | MVP (credits + preview) |
| Free tier | "Start creating free — 50 designs per month, no credit card" (S13); free exports watermarked (S20). | Free tier: fixed monthly credit grant, watermarked exports, Direct mode only. | MVP |
| Commercial rights | Paid generations include full commercial usage rights (S9, S7). | Same policy; stated per-plan in export dialog. | MVP |

---

## 3. Public-source discrepancies worth tracking

1. **MCoT expansion**: "Mind Chain of Thought" (S4, S8) vs "Multi-Chain of Thought" (S5) — Lovart's own pages disagree. Treat MCoT as a marketing label for a plan-then-generate loop, not a documented architecture.
2. **"Tab" semantics**: options gallery you click (S16, S21) vs keyboard-key quick-edit menu (Scribd-mirrored architecture doc; S15's "press Tab" phrasing). Atelier commits to one behavior: variant grid + Tab-key cycling.
3. **PSD export**: official pages list PSD (S1, S7); ReviewNexa says exports are flattened, layers lost (S20). Either PSD is flattened or the review predates the feature. Atelier's layered-PSD line item is scoped as P2 with an explicit acceptance test.
4. **Model roster churn**: reviews across 2025–2026 cite different rosters (GPT-Image/Flux/Ideogram/Kling in S19 vs Nano Banana Pro/Seedream/Veo/Sora in S8-S9). Conclusion: the roster rotates quarterly. Atelier's adapter-based Router is designed for exactly this churn.

## 4. Where Atelier deliberately diverges

- **Editable plan**: Lovart shows a task chain; Atelier lets users delete/reorder plan steps before execution.
- **One edit tool, three entry points** instead of Touch Edit / Region Editing / Edit Elements as separate named features.
- **Layered exports as a testable promise** (P2), where Lovart's public record is contradictory.
- **No proprietary-model marketing**: the Router advertises the real engine name on every output (Lovart does show model names above results per S21 — we keep that, and extend it to the export metadata).
- **Fewer modalities at launch** (no 3D, no audio at MVP) in exchange for reliability of the image loop, which is where Lovart's reviewers report the value concentrates (S20: "the interactive canvas alone justifies the price").
