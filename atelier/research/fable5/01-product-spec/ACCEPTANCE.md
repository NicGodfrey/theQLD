# ACCEPTANCE.md — Atelier MVP must-haves vs later parity

Criteria are binary and testable. "Lovart parity" claims map to the public evidence indexed in
`FEATURE_MATRIX.md` §1 (S-numbers). MVP ships when every M-item passes; P2 items are sequenced
parity/differentiation work, not vague futures.

---

## MVP — must have (M-items)

### M-1 Project & canvas
- [ ] Create project → empty infinite canvas in ≤ 2 s; sign-up → first generation ≤ 2 min with no required onboarding steps (beats Lovart's reported 2m47s, S20).
- [ ] Canvas holds ≥ 200 asset nodes at 60 fps pan/zoom on a mid-range laptop (Lovart's "all assets in one workspace" claim, S1/S3, made measurable).
- [ ] No cap on project count; credits are the only constraint (parity with S20).
- [ ] Threads: ≥ 2 independent chat threads per project, each with isolated context ledger.

### M-2 Chat & agent (Helix)
- [ ] Plan mode: brief → visible plan card; user can delete or reorder steps; run executes only remaining steps. (Differentiator over S21's read-only task chain.)
- [ ] Plan mode planning latency ≤ 15 s before first generation starts (Lovart's stated MCoT pause is 5–15 s, S2/S3).
- [ ] Underspecified brief triggers ≤ 3 clarifying questions in one grouped card; "use defaults" always available; agent never blocks on unanswered questions (S4 parity + escape hatch).
- [ ] Direct mode: prompt → first pixels < 15 s median, no plan, no questions (Fast Mode parity, S3).
- [ ] Mode toggle usable on every turn without losing draft prompt text (S3: switchable at any point).
- [ ] Referring-expression test set: 20 scripted follow-ups ("make the logo bigger", "darker background on the second poster") resolve to the correct node ≥ 90% of runs; resolution target is always displayed before the edit applies.

### M-3 Generation
- [ ] ≥ 2 image engines behind the Router; auto-choice logged with reason; manual override dropdown per prompt (S8/S18 parity).
- [ ] Engine name visible on every node, in chat, and in export metadata (extends S21).
- [ ] Credit cost displayed before every generation; generation cannot fire without it (S11 parity). Failed generations auto-refund.
- [ ] Plan mode returns a Pick grid of 4 variants, each with a one-line rationale (S1/S4 parity); Tab/arrow cycling, Enter to keep; discarded variants recoverable from the node's variant stack.
- [ ] 1 video engine: text-to-video and image-to-video, ≤ 10 s clips, 1080p, MP4 export (floor of the S9/S23 roster).

### M-4 Editing
- [ ] Spot Edit: click-to-mask + instruction re-renders only the masked region; pixels outside the mask byte-identical. Auto-mask acceptance: ≥ 85% correct-mask rate on a 100-image benchmark (beats the ~80% reviewer-reported Touch Edit reliability, S20); manual brush fallback always present.
- [ ] Text layers: click-to-edit real text; retype preserves font, size, position (S20 parity).
- [ ] Background removal as a one-click canvas verb (S20 parity).
- [ ] Node-scoped undo ≥ 50 steps; project snapshot on every agent turn; snapshot restore ≤ 5 s.

### M-5 Brand (StyleLock)
- [ ] Create kit: logos (SVG/PNG), palette (hex + role labels), fonts, tone notes. Multiple kits per workspace (S7/S12 parity).
- [ ] Project-default kit selector (canvas upper-left) AND per-turn `@` mention override — both scopes, matching Lovart's documented behavior exactly (S12).
- [ ] Compliance check: with a kit active, generated palettes hit kit colors within ΔE ≤ 10 for ≥ 90% of a 50-generation benchmark; violations flagged on the node by the critic pass.
- [ ] Shelf: upload asset once, `@` mention it in a different project (S12 parity).

### M-6 Export & plans
- [ ] Image export: PNG (incl. transparent), JPEG, SVG for vector-text nodes, PDF-RGB. Video: MP4/H.264. (MVP floor of S1/S7 roster.)
- [ ] Free tier: fixed monthly credit grant, watermarked exports, Direct mode only (S13/S20 pattern).
- [ ] Paid tiers: watermark-free, full commercial-rights statement in the export dialog (S9 parity).
- [ ] Credit ledger: per-turn history showing engine, action, cost (S11 parity).

### MVP exit bar (aggregate)
- [ ] Scripted end-to-end run — brief → plan → 4 variants → 2 Spot Edits → kit swap → PNG+PDF export — completes in ≤ 10 min with zero support intervention, executed by 5 external testers unfamiliar with the product.

---

## P2 — later parity & differentiation

Ordered; each has an entry test.

### P2-1 Multi-engine depth
- [ ] ≥ 4 image engines, ≥ 3 video engines (approaching the S8/S9 roster: Sora/Veo/Kling/Hailuo/Wan/Seedance-class breadth). Entry test: Router A/B shows measurable win-rate differences per task type, logged per generation.
- [ ] Video controls: keyframes, camera/motion parameters, vertical/square/landscape cuts (S10 parity); 4K upscaler (S9 parity).

### P2-2 Audio & 3D
- [ ] Music beds + SFX via one licensed engine; audio attaches to video nodes; separate `sfx_`/`mus_` labeling in the Shelf (S13/S14/S17 parity).
- [ ] TTS voiceover on video nodes (S13 parity).
- [ ] Text/image-to-3D preview node with GLB export (S17's Tripo-class floor). No 3D editing.

### P2-3 Layered exports (contested-claim differentiator)
- [ ] PSD export with real text layers and separated image layers; acceptance: file opens in Photoshop with ≥ 3 independently editable layers for a benchmark poster. This is the test Lovart's public record cannot currently pass (official PSD claim S1/S7 vs "exports are flattened" S20).
- [ ] PDF CMYK + bleed with configurable bleed margin (S7 parity).

### P2-4 Scale-out workflows
- [ ] Fanout: master design → ≥ 7 platform sizes in one export job (matches the 7-platform/21-asset workflow and 20+ variant batch export reported in S20).
- [ ] Sweep: single-variable N-way strips (palette/font/background) without regenerating the subject (the quick-edit reading of "Tab", FEATURE_MATRIX §3.2).
- [ ] Character consistency: same subject across ≥ 5 generations with recognizable identity (Lovart ships this imperfectly per S20's v2.1 note — entry test is a side-by-side human eval, ≥ 70% same-person judgment).

### P2-5 Team & platform
- [ ] Shared workspaces: shared projects + shared kits (Lovart Team plan direction, S11/S20).
- [ ] Public API with project/thread management and generation endpoints, keyed auth (Lovart precedent: lovart-skill OpenAPI with HMAC AK/SK, S17).
- [ ] Web-research step available inside Plan mode (S10 parity).
- [ ] Relax-style off-peak queue — only if unit economics support owned/reserved GPU capacity (S11's Unlimited Relax Generation); otherwise permanently out of scope.

### Explicit non-goals (recorded so parity pressure doesn't creep)
- No template library (Lovart is positioned agent-first, not template-first; S5 contrasts it with Canva).
- No proprietary-model branding; engines are always named.
- No stylized-art/anime specialization — Lovart's own reviewers place this outside the category's strength (S19); Atelier stays commercial-design-first.
