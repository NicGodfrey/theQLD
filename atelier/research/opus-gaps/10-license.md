# 10 — Licensing, IP and ship-safety gaps

Opus#10 of 10. Read-only audit of `/workspace` at `cursor/atelier-byok-studio-d639`
(`6515594`). Scope: `atelier/integrations/ADAPTERS.md`, `atelier/integrations/TOP100.md`,
both TOP100 data files, `research/fable5/09-oss-adapters/`, and a contamination sweep of
the live `atelier/helix/` + `atelier/web/` trees and every research stub.

Not legal advice. Every license fact below was re-verified against primary sources on
2026-08-21 (see §11); the repo's own docs instruct exactly that ("Re-verify before any
release"), and three of the facts had drifted or were stated imprecisely.

---

## 1. Verdict

**Nothing is contaminated today. The documents that are supposed to keep it that way are
contradicted by the data files shipped next to them.**

Two findings drive everything else:

1. **The clean-room story holds.** I found zero lines of third-party code in the live
   tree or in any research stub. The only occurrences of `tldraw`, `konva`, `litellm`,
   `comfy` etc. in `.py`/`.js` files are docstrings and catalog rows (§2). The
   patterns-not-packages discipline in `research/fable5/09-oss-adapters/ADAPTERS.md` is
   real and was actually followed.
2. **The shipped catalog tells a future contributor to break it.** `atelier/data/top100.json`
   — the file `README.md` and the public `atelier.html` both link to, and the one
   `tests/test_helix.py` asserts against — carries 19 `NOASSERTION` rows, 13 copyleft
   rows, and integration instructions that directly contradict `ADAPTERS.md`, including
   "Helix canvas **is** a tldraw instance", "worth **porting**" next to a GPL-3.0 project,
   and an in-process AGPL pip package with no warning at all (§4).

The ship-blocking gap is therefore not "someone vendored something." It is that **the
repo has no LICENSE file at all** (§3), no notices file, no output-rights statement, no
BYOK terms, and a machine-readable catalog whose license column is wrong often enough
that it cannot be used for the compliance decisions it is shaped to support.

Severity legend: **B** blocker for v1 ship · **M** major · **m** minor.

---

## 2. Contamination sweep — clean, and here is the evidence

| Check | Result |
|---|---|
| Third-party source trees under `atelier/` | none |
| `node_modules/`, `vendor/`, `*.min.js`, `*.min.css` anywhere in repo | none |
| Upstream identifiers in executable lines (not comments/docstrings) | none; only catalog data rows in `data/build_top100.py` and `tests/test_helix.py` |
| Copyright/SPDX headers from third parties | none (the only `Copyright` strings in the repo are theQLD's own footers) |
| `package.json` / bundler config | none — the zero-npm rule is genuinely enforced by absence |
| Live `web/index.html`, research `06-board-ui/index.html` | no external `<script>`; local `styles.css`/`app.js` only |

Spot-read of the two stubs most at risk of being paraphrase-close to their inspirations:

- `stubs/js/store.js` (122 lines) — generic `Map` + change-set listeners + inverse-patch
  stacks. Records-store-with-diff-listeners is an architecture, not tldraw's expression.
  It even declines the obvious tldraw vocabulary beyond `mark()`.
- `stubs/js/scene.js` (111 lines) — `version`/`versionNonce`/`isDeleted` LWW is
  excalidraw's *scheme*, and excalidraw is MIT anyway, so copying would have been legal.
  Its `indexBetween()` is a from-scratch base-36 midpoint that the comment honestly
  labels as not the jitter-hardened reference algorithm.

**Residual risk is provenance, not code.** There is no `CONTRIBUTORS`/DCO, no CLA, no
commit trailer discipline, and the whole tree was authored by agents. If someone later
alleges copying from tldraw or Open WebUI, the defence today is "trust the comment
headers." That is thin for a company-owned repo. **[M]** Fix: a `PROVENANCE.md` recording
that stubs were written against public documentation, plus a per-file `SPDX-FileCopyrightText`
+ `SPDX-License-Identifier` header once a license exists (§3).

---

## 3. No LICENSE anywhere in the repo — the actual blocker **[B]**

`find` across the whole repo returns **zero** files matching `*LICENSE*`, `*COPYING*`,
`*NOTICE*`, or `*THIRD*PARTY*`. Not at the root, not in `atelier/`.

Consequences, in order of how soon they bite:

1. **`atelier/` is "all rights reserved" by default.** Nobody — including a contractor,
   a future employee, or a user who downloads the tree from the public site — has any
   right to copy, modify or run it beyond what copyright grants by default. The README's
   `python3 -m atelier` invitation and the public page's "Launch locally" instruction
   grant nothing in writing.
2. **The permissive positioning is unbacked.** `ADAPTERS.md` §2 justifies the ideas-only
   tldraw stance to avoid "contaminat[ing] our permissive positioning." There is no
   permissive positioning to protect until a license file exists. The argument is
   currently load-bearing on a file that does not exist.
3. **`THIRD_PARTY_NOTICES.md` is promised and absent.** `ADAPTERS.md` closes by
   committing to ship it "once dependencies exist." Dependencies already exist in the
   *site* (jQuery 1.12.2, Font Awesome 4.7, Poppins via Google Fonts — all fine to use,
   Font Awesome waived attribution back at 3.0, but none are recorded anywhere).
4. **Ambiguous ownership boundary with the host repo.** The root is a commercial legal
   directory owned by The Queensland Legal Directory Ltd (ACN 651 170 580). A reader
   cannot tell whether `atelier/` is company IP under the same reservation, or an
   intended open-source project. That ambiguity is the thing that kills later relicensing.

**Fix (v1, small and mechanical):**

- `atelier/LICENSE` — MIT or Apache-2.0. Prefer **Apache-2.0**: it carries an explicit
  patent grant and a `NOTICE` mechanism, and it is the license most compatible with the
  "we take Apache-2.0 things like Outlines and the official SDKs" posture. MIT is
  acceptable and shorter; do not leave it unstated.
- `atelier/THIRD_PARTY_NOTICES.md` with two sections: *dependencies* (empty today — say
  so explicitly, it is a feature) and *pattern acknowledgements* (the eight projects in
  `ADAPTERS.md`, each with "architecture referenced, no code used").
- Root `LICENSE` decision recorded even if the answer is "site content is proprietary,
  `atelier/` is Apache-2.0" — mixed-license repos are normal, silent ones are not.
- Per-file SPDX headers in `atelier/**` so the boundary survives file moves.

---

## 4. The catalog contradicts the policy — the "just vendors" attack surface **[B]**

`ADAPTERS.md` (research) covers **8** projects in depth. `integrations/ADAPTERS.md` (live,
23 lines) covers ~10 in one table. The shipped catalog lists **100**, with per-row
`integrate_as` instructions written in the imperative. When those two disagree, the
100-row machine-readable file is what a contributor or coding agent will act on.

They disagree in ways that would be expensive:

| Catalog row (`integrate_as`) | Policy says | Why the row is dangerous |
|---|---|---|
| tldraw: "The board itself: Helix canvas **is a tldraw instance** with custom asset/gen-node shape types" (`top100.live.json`) | "**Ideas only, never code**" | Straight inversion. Since SDK 4.0 the tldraw SDK refuses to run in production (HTTPS + non-localhost + `NODE_ENV=production`) without a key. A hobby key is **non-commercial only** and discretionary; theQLD is a for-profit ACN entity, so the only path is a commercial license at value-based pricing negotiated with sales. Also breaks the React/zero-npm rule. |
| Fooocus (GPL-3.0): "its GPT-2 prompt expansion is **worth porting** into spokes" | ComfyUI-class GPL is HTTP-out-of-process only | "Porting" GPL-3.0 code into `helix/spokes/` makes Atelier a derivative work → GPL-3.0 for the whole thing. This is the single most likely accidental-copyleft event in the repo, because it reads as an endorsement. |
| Remotion: "**Loom's motion-graphics compositor**: templated brand intros/outros" | `FUTURE.md`: "Do not integrate Remotion now" | Presented as a wired component with no licensing caveat in the row itself. |
| `ultralytics/ultralytics` (AGPL-3.0, rank 92, shipped `top100.json`): "layout detect later" | not mentioned in `ADAPTERS.md` at all | The worst landmine in the tree. `pip install ultralytics` is in-process, in a server. Ultralytics' own licensing page states an Enterprise License is required for "SaaS platforms, APIs, or cloud systems that use YOLO behind the scenes", "internal business tools", and "custom-trained or fine-tuned YOLO models in a proprietary setting", and their maintainers state on the tracker that AGPL compliance requires publishing the complete corresponding source of the whole app **publicly** — and that fine-tuned weights are derivative works. One `import` flips Atelier to AGPL-3.0 or an invoice. |
| `minio/minio` (AGPL-3.0, rank 79): "future object store" | not mentioned | Bundling/redistributing MinIO as Atelier's artifact store puts an AGPL network-service program in the ship. Safe only as a user-supplied S3-compatible endpoint reached over HTTP — same posture as ComfyUI, but nothing says so. |
| `coqui-ai/TTS` "MPL-2.0": "**XTTS-v2** for quick voiceover drafts" | not mentioned | Code/weights split missed. The toolkit is MPL-2.0, but XTTS-v2 **weights** are under the Coqui Public Model License, which "allows only non-commercial use of a machine learning model **and its outputs**" — and Coqui Inc. dissolved in January 2024, so no commercial license can be bought at any price. A design tool whose users sell deliverables cannot ship this. Permissive substitutes: Piper (MIT), Kokoro (Apache-2.0), Chatterbox (MIT). |
| `fishaudio/fish-speech`: "where its research license fits the deployment" | not mentioned | Weights are CC-BY-NC-SA: non-commercial **and** share-alike. "Where it fits" is not a policy; for a commercial design tool it never fits. |
| `KlingAIResearch/LivePortrait`: "Talking-head/avatar spoke: animate brand mascots and **spokesperson stills**" | `ADAPTERS.md` hard-no: "Deepfake / non-consensual face-swap tools" | The catalog wires in the exact capability the hard-no list bans, with restricted weights on top. Under EU AI Act Art. 50(4) (in force, §8) deployer deepfake disclosure applies; Australia criminalised non-consensual sexual deepfakes in 2024. A row that says "animate spokesperson stills" needs a consent gate or deletion. |
| `simple-icons` (CC0-1.0): category "brand-kit" | not mentioned | CC0 is a **copyright** waiver on the SVG path data. The logos remain trademarks; simple-icons' own DISCLAIMER says it "cannot be held responsible for any legal activity raised by a brand" and asks users to check each brand's guidelines. A tool that drops third-party logos into user-generated marketing assets creates trademark and passing-off exposure that no file license touches. |
| Hunyuan rows: "community license permits <100M MAU commercial use" | not mentioned | Half right and therefore worse than silence: Tencent's community licenses also carry territorial exclusions, an acceptable-use policy, and attribution/naming obligations for derivatives. |
| `Arize-ai/phoenix` (ELv2), `n8n` (SUL-1.0), `dify` (Apache+conditions), `lobehub` (Community License) | not mentioned | All four forbid offering the software to third parties as a hosted service. Fine as internal tooling or user-supplied endpoints, breach if bundled into a hosted Atelier. None of the rows say which. |
| Open WebUI: "Reference for BYOK settings UX" | "UX patterns only, no code/assets" | Row is directionally fine; the live `integrations/ADAPTERS.md` understates it as "BSD-3 with a branding clause." Precisely: the clause forbids altering/removing/obscuring Open WebUI branding in any deployment or distribution unless ≤50 end users in a rolling 30 days, written permission, or an enterprise license. Reusing their code under an "Atelier" brand is the targeted scenario. |
| `photopea/photopea`: "touch-edit inspiration", logged `NOASSERTION` | — | Photopea is proprietary. `NOASSERTION` reads as "unknown," which invites investigation rather than warning against it. |

Also: `integrations/ADAPTERS.md` still ships an unresolved TODO in the license column —
`| Langfuse | Usage event shape | Their cloud | **Check license** |`. The live catalog
resolved it ("MIT (core) + ee"); the live doc did not.

**Fix:** the catalog's `integrate_as` field must not be the only integration instruction.
Add a mandatory `boundary` enum to every row (§9) and make the doc/data disagreement a
test failure.

---

## 5. License metadata is not fit for compliance use **[M]**

Two catalogs coexist and disagree, and the wrong one is wired:

| | `data/top100.json` (shipped, wired, linked from README + public page, asserted by `tests/test_helix.py`) | `data/top100.live.json` (GraphQL re-verified 2026-08-21) |
|---|---|---|
| `NOASSERTION` rows | **19** | 0 |
| Distinct license strings | 8 | 24 |
| tldraw | `NOASSERTION` | `tldraw License (free with watermark)` |
| konva, paper.js | `NOASSERTION` | (both actually MIT) |
| litellm | `NOASSERTION` | `MIT (core) + enterprise dir` |
| ultralytics (AGPL), minio (AGPL) | present, unflagged | silently dropped |

Problems this creates:

- **`NOASSERTION` is GitHub's "our detector failed", not a license.** Nineteen rows in the
  shipped file are unknowns presented in a column that looks authoritative. Several are
  in fact permissive (konva, paper.js, `vercel/ai`, pytorch), one is proprietary
  (photopea), one is non-OSI-with-a-key (tldraw), one is dual GPL/LGPL-by-build (FFmpeg).
- **The live file's improvements never reached the shipped file**, and the two AGPL rows
  that most needed a warning were removed rather than annotated — so the correction lost
  information.
- **Stars are stale and unsourced in the shipped file** (`stars_approx` hardcoded in
  `build_top100.py`), which matters only because it signals the whole file is a snapshot
  someone typed, not a verified record.
- **No `checked_at` per row.** `captured_at` is file-level, so a row cannot be aged out.

**Fix:** one catalog. Regenerate `data/top100.json` from the live pipeline, add per-row
`license_spdx`, `license_note`, `boundary`, `checked_at`, keep `NOASSERTION` **only** as
`license_spdx: null` plus a mandatory human `license_note`, and never drop a risky row —
mark it `boundary: forbidden` with the reason.

---

## 6. Product packaging: should Atelier live in the legal-directory repo forever? **[M]**

Facts: the repo root is theqld.com (`CNAME`), a GitHub Pages site for a registered
Australian company selling legal-directory services. `atelier/` is 15 commits of a
Python/BYOK desktop app inside it, surfaced by `atelier.html` in the site's main nav
between DIRECTORY and ABOUT.

Why this is a licensing/packaging problem and not just tidiness:

1. **Pages serves the whole repo.** There is no `_config.yml`, no exclude list, no
   workflow. Default Pages publishes every non-underscore file at the site root, so
   `atelier/helix/keyring.py`, the entire `research/fable5/` tree, and every internal
   threat model are almost certainly fetchable at `theqld.com/atelier/...`. *(I could not
   confirm from this sandbox — egress to theqld.com is blocked. **Verify first**; it is a
   one-curl check.)* Publishing source is fine when you meant to; publishing it under an
   all-rights-reserved silence (§3) from a law-adjacent commercial domain is not a
   decision anyone made.
2. **Two legal identities on one origin.** Same domain, same `style.css`, same footer
   ACN. A user who pastes an OpenAI key into something served from a legal-directory
   company's domain will reasonably read theQLD's privacy policy and disclaimer as
   governing it. Neither mentions AI, models, API keys, or generated content (§7, §8).
   The site's own disclaimer is about legal-referral content.
3. **Relicensing gets harder every commit.** Untangling a subdirectory into its own
   Apache-2.0 repo is easy now (15 commits, one author entity). It is a chore after
   external contributors, and a negotiation after a CLA-less community forms.
4. **Release engineering has nowhere to go.** `README.md` says run `python3 -m atelier`
   from the repo root; there is no `pyproject.toml`, so the only supported install is
   "clone a law directory." The other Opus slices flag the same thing as a UX blocker;
   from here it is also the reason no license or notices file has an obvious home.

**Recommendation for v1: keep the subdirectory, but make it a *package* with hard edges,
and plan the split.**

- Now: `atelier/LICENSE`, `atelier/THIRD_PARTY_NOTICES.md`, `atelier/pyproject.toml`
  (name, version, license, `console_scripts`), and a Pages exclude so the site publishes
  only `atelier.html` — not the source tree — unless publishing is the intent.
- `atelier.html` gains one line: "Atelier is a separate open-source project by
  <entity>; it is not a legal service and the directory's terms do not apply to it,"
  linking to Atelier's own terms (§8).
- Trigger for extraction to its own repo: the first external contributor, the first
  released artifact (PyPI/installer), or any hosted deployment — whichever comes first.
  Extraction is cheap only while all three are false.

**Brand exposure while we are here [m]:** README says "Lovart-class", `ARCHITECTURE.md`
and `atelier.html` say "inspired by Lovart's public product", `openai_spoke.py` ships the
user-facing string "not Lovart credits", and `README.md` writes "OpenAI / ChatGPT API".
Comparative reference to a competitor is normally defensible nominative use, and the
"does not clone Lovart code/private APIs" disclaimers are exactly the right instinct. But
"X-class" in the product's own tagline, on a commercial site, is positioning-by-someone-
else's-mark. And "ChatGPT API" is not an OpenAI product name; OpenAI's brand guidelines
restrict using their marks in ways implying affiliation. Cheap fix: describe the product
by capability ("chat-driven infinite-canvas design agent"), keep competitor names to a
single comparison sentence, and say "OpenAI API" everywhere. Keep the accurate and
valuable "ChatGPT Plus is not API access" clarification — just do not brand with it.

---

## 7. No statement about rights in generated assets **[B]**

Atelier's entire purpose is producing commercial deliverables — logos, posters, brand
kits, per the `10-eval` fixtures. Nowhere does the repo say what a user owns or may do
with an output. For a design tool this is the most-asked question and the most expensive
one to answer wrong. The gap has four independent layers:

1. **Provider terms attach to the user, not to us.** Under BYOK the call goes from the
   user's machine to their own account, so their agreement with OpenAI/Google governs
   the output. OpenAI's terms assign output rights to the customer. Google's Gemini API
   terms do not claim ownership — **but** on Unpaid Services (AI Studio keys, unpaid
   Gemini quota) "Google uses the content you submit … and any generated responses to
   provide, improve, and develop Google products … and machine learning technologies,"
   and "human reviewers may read, annotate, and process your API input and output," with
   an explicit instruction not to submit confidential information. Atelier's onboarding
   sends users to `aistudio.google.com/apikey` — i.e. the free tier — and its core loop
   is *upload the client's brand material and iterate*. **A designer uploading a client's
   unreleased identity to Atelier with a free Gemini key is putting it into Google's
   training and human review, and nothing in the product says so.** That is a
   confidentiality disclosure, not just a licensing one.
2. **Outputs may have no copyright at all.** Under current US practice (Copyright Office
   2025 guidance; *Thaler* affirmed on appeal) and Australian authority (*IceTV*,
   *Telstra v Phone Directories*, *Acohs v Ucorp* — human authorship required, and
   Australia has no fair-use safety valve), purely prompt-generated output is likely
   unprotectable. A client paying for a logo usually wants an assignable exclusive right.
   Silence here becomes a warranty dispute, and it argues for keeping human-edited layers
   and recording which parts were hand-authored.
3. **Marking obligations now apply.** See §8.
4. **Model-license reach-through.** Some weights license the *outputs*, not just the
   code: CPML (XTTS-v2) restricts "the model **and its outputs**" to non-commercial;
   CC-BY-NC-SA weights (fish-speech) restrict outputs too. If a spoke uses such a model,
   the user's deliverable is encumbered by a term they never saw. Any model whose license
   reaches outputs must be `boundary: forbidden` for the default install.

**Fix:** `atelier/OUTPUT_RIGHTS.md` (short, linked from the UI's export/download path):
we claim nothing in your outputs; your rights come from your provider's terms, so read
them; free-tier Gemini keys mean Google may train on and human-review your prompts and
outputs — use a billing-enabled key for client work; AI-only output may not be
copyrightable in AU/US; images from Google models carry SynthID provenance and you must
not strip it; models with non-commercial or output-reaching licenses are excluded from
the default install and any opt-in ones warn at enable time.

---

## 8. AI Act marking and disclosure — live obligations, unaddressed **[M]**

Article 50 of the EU AI Act **applies from 2 August 2026** — three weeks before this
audit. It reaches non-EU providers whose systems are placed on the EU market or whose
outputs are used in the EU, with penalties up to €15M or 3% of worldwide turnover.

What lands on a tool like Atelier:

- **Provider marking duty, Art. 50(2):** systems generating synthetic image/audio/video/
  text must mark outputs in a machine-readable format and make them detectable. Systems
  placed on the EEA market **before** 2 Aug 2026 have until **2 December 2026**; anything
  placed after must comply from the outset. A v1 shipping now is in the second bucket.
- **Deployer deepfake disclosure, Art. 50(4):** relevant the moment a talking-head or
  face-animation spoke exists (§4, LivePortrait row).
- **Practical wrinkle for this design:** you can lean on the upstream provider's marking
  for images — Gemini/Imagen image output carries SynthID — but **Gemini API *text*
  output is not SynthID-marked and carries no machine-readable provenance signal**
  (confirmed by Google staff on the developer forum; text watermarking is app-only and
  not planned for the API). So an Atelier that emits generated copy, alt text or captions
  cannot inherit compliance and must mark them itself.
- The Commission's voluntary **Code of Practice on Transparency of AI-generated Content**
  offers a presumption-of-conformity path; non-signatories must demonstrate equivalence.

**Fix, cheap version, v1:** write C2PA-style or at minimum embedded metadata provenance
on every artifact at the single choke point that already exists —
`helix/loom.py:write_bytes()` is the one function all bytes pass through. Record model,
provider, timestamp, and "AI-generated"; preserve any upstream SynthID/C2PA rather than
re-encoding it away; never strip provenance on export; add a `GENERATED_CONTENT.md`
noting the EU position and the 2 Dec 2026 date. Also note the trap: the demo SVG
(`loom.py:demo_svg`) is *not* AI-generated and must not be marked as such — and per other
slices it is currently passed off as a successful generation, which is a labelling problem
as well as a UX one.

---

## 9. No BYOK user terms **[B]**

The product's entire pitch is "paste your API key." There is no ToS, no AUP, no warranty
disclaimer, no liability cap, and no statement of the key-handling promises that
`research/fable5/08-security-quota/POLICY.md` already makes internally. `POLICY.md` is
genuinely strong — never log raw keys, no reveal endpoint, redaction backstop with a
counter, canary-key CI grep — and **none of it is stated to the user**, which wastes it:
those are exactly the commitments that make a stranger willing to paste a key.

Missing, in rough order of value:

| Term | Why it matters here |
|---|---|
| Warranty disclaimer + liability cap | Whatever license §3 lands on carries "AS IS", but that covers the *software*, not the *service* or advice-shaped output. A design tool that outputs a logo containing someone else's trademark needs this. |
| Spend is the user's | Keys spend the user's quota. A runaway loop is real money. Say the budget gate is best-effort and the user owns the bill. |
| Key handling, stated | Surface `POLICY.md`'s guarantees: stored locally at `~/.atelier/keyring.json` mode 0600, never returned by the API, never logged, no reveal feature, re-paste if lost. |
| Provider terms flow through | The user must comply with OpenAI/Google usage policies; Atelier is not a party and cannot grant rights the provider withholds. |
| Free-tier training/human-review warning | §7(1). Needs to be at key-entry time, not buried in a doc. |
| Acceptable use | Mirror the `ADAPTERS.md` hard-no list into user-facing terms: no deepfakes/non-consensual imagery, no trademark or copyright laundering, no unofficial-endpoint or quota-bypass configuration. Today the hard-no list binds only developers. |
| Optional-endpoint warning | The "optional OpenAI-compatible host you set explicitly" escape hatch lets a user point Atelier at a reverse proxy — the exact thing the architecture forbids. The warning belongs where the field is. |
| No professional advice / not part of the directory | §6(2). Especially given the domain. |
| Governing law | Australian Consumer Law guarantees cannot be excluded for consumer supplies; a boilerplate US-style disclaimer would be partly void. Needs the standard ACL carve-out wording. |

**Fix:** `atelier/TERMS.md` (plain language, one page) plus a first-run key-entry panel
that states the four things that matter — your key stays local, your quota pays, free
Gemini keys are trained on, outputs are yours subject to your provider — with a link.

---

## 10. Recommended ship-safe integration policy for v1

Design goal: make the *safe* path the *easy* path, and make the unsafe path fail in CI
rather than in a letter. Six rules, then the enforcement.

### R1 — Every third-party project gets exactly one boundary label

Replace prose judgement with a closed enum, stored per catalog row and repeated in
`ADAPTERS.md`:

| `boundary` | Meaning | Allowed licenses | Obligation |
|---|---|---|---|
| `pattern` | Architecture/UX ideas from public docs. Zero bytes. | any, including proprietary | acknowledge in notices |
| `dependency` | Pinned package, in-process | MIT / BSD / Apache-2.0 / ISC / MPL-2.0 (unmodified files only) | license text in notices; pin exact version |
| `single-file-vendored` | One prebuilt UMD/JS artifact, header intact | MIT / BSD / Apache-2.0 | full text + provenance comment |
| `subprocess` | Invoked via argv/pipes, user-supplied binary | GPL / AGPL / LGPL ok | never redistribute the binary; document install |
| `network-worker` | User-installed service over HTTP | GPL / AGPL / ELv2 / SUL / Community ok | user brings their own; we ship only a client + our own templates |
| `opt-in-plugin` | Off by default, user accepts upstream terms at enable time | non-OSI, seat/size-tiered (tldraw, Remotion) | in-UI license notice + link before first use |
| `forbidden` | Do not integrate, in any form | — | row must state why |

Nothing is integrated without a label. "It's just a small copy" is not a label.

### R2 — Hard-forbidden list, promoted from prose to data

`forbidden` in v1, each with the reason in the row so the next person does not re-litigate:

- **Any copyleft code in-process.** Ultralytics (AGPL — pip-installable, therefore the
  most likely accident), MinIO-as-bundled-store, `nebula-nodes`, `new-api`, and *porting*
  anything from Fooocus/A1111/ComfyUI/chatbox. GPL/AGPL projects are reachable only as
  `network-worker` or `subprocess`.
- **Any model whose license reaches outputs or forbids commercial use.** XTTS-v2 (CPML),
  fish-speech weights (CC-BY-NC-SA), gaussian-splatting (Inria non-commercial),
  LivePortrait restricted weights. Substitute permissive weights (Piper/Kokoro/Chatterbox
  for voice; gsplat for splatting) or drop the capability.
- **Face/voice reenactment of real people** — already in the hard-no list; delete the
  catalog row that contradicts it, or gate it behind explicit consent capture plus Art.
  50(4) disclosure.
- **Third-party brand logos as generatable assets.** simple-icons stays a `pattern`
  reference; do not ship a logo library users can drop into deliverables.
- **Unofficial provider endpoints, cookie/quota-bypass proxies.** Already policy; move it
  into user terms too (§9).

### R3 — Non-OSI, seat-tiered tools are `opt-in-plugin` behind a generic contract, never a default

tldraw and Remotion are both genuinely good and both cost money at theQLD's size. Keep
`FUTURE.md`'s instinct — define the generic contract first (`render-worker`:
`POST /render {composition, props} → mp4`; board engine behind an interface), so the
permissive option (canvas+ffmpeg, Motion Canvas MIT) is the default and the licensed one
is a swap.

Two precision corrections to `FUTURE.md` worth folding in, because they change the
conclusion's *reasoning* even though the conclusion stands:

- **tldraw:** the doc says hobby use "requires a visible watermark." True but incomplete —
  hobby licenses are **non-commercial only** and discretionary, so they are unavailable to
  a for-profit entity regardless of watermark willingness. The real options are a 100-day
  trial or a negotiated annual commercial license. Say that, or someone will assume
  "watermark = free."
- **Remotion:** the doc says shipping Remotion "would silently impose that obligation on
  our users." For a *hosted* app that is not right — Remotion's FAQ says end users of a
  web app built on Remotion are not Users and do not count toward the threshold. But
  Atelier is distributed as a **local** app the user installs and runs, which makes the
  user the operator, so **the conclusion holds for exactly this product** and would flip
  if Atelier ever became hosted. Record the reason, not just the verdict; the trigger for
  re-analysis is the packaging change.

### R4 — One catalog, machine-checked

- Delete `data/top100.json`-as-hand-typed. Regenerate from the live pipeline; keep one
  file as the source of truth and point README, `atelier.html`, and `tests/test_helix.py`
  at it.
- Required per row: `license_spdx` (nullable), `license_note` (required when null or when
  the SPDX id is not the whole story — dual code/weights, `ee/` dirs, branding clauses),
  `boundary`, `checked_at`.
- Never delete a risky row. `boundary: forbidden` + reason preserves the warning.
- Test: every row has a `boundary`; no row with a copyleft/non-OSI/null license has
  `boundary` in {`dependency`, `single-file-vendored`}; every `forbidden` row has a reason.
  That one test converts §4's whole table into a build failure.

### R5 — Provenance and notices are part of the build

- `THIRD_PARTY_NOTICES.md` generated from the catalog + the dependency lock, not hand-kept.
- SPDX headers on every `atelier/**` source file.
- CI greps for vendored-code smells: `Copyright (c)` from a non-theQLD holder, `*.min.js`,
  `node_modules`, `package.json` (the zero-npm rule made executable), and known upstream
  identifiers in non-comment lines.
- `PROVENANCE.md` recording the clean-room method for the stubs (§2).

### R6 — Output-side compliance at the single choke point

Provenance metadata written in `loom.py:write_bytes()`; upstream SynthID/C2PA preserved
on any re-encode; export path never strips marks; demo-SVG output labelled as demo, not
as generated. Fonts: everything today is a system font stack (`Georgia, serif`,
`ui-sans-serif`), so there is no issue yet — but the moment export **embeds** a font
(PDF, or the `fontsource` brand-kit pinning the catalog already contemplates), embedding
rights become a per-font question. Restrict embeddable fonts to OFL/Apache families and
record them in notices before the first PDF export ships.

### Ordered v1 cut list

| # | Action | Sev |
|---|---|---|
| 1 | `atelier/LICENSE` (Apache-2.0 recommended) + root license boundary stated | B |
| 2 | `atelier/TERMS.md` + first-run key-entry disclosures (§9) | B |
| 3 | `atelier/OUTPUT_RIGHTS.md` + free-tier Gemini training/human-review warning at key entry | B |
| 4 | Fix the four contradicting catalog rows: tldraw "is a tldraw instance", Fooocus "worth porting", Remotion "Loom's compositor", LivePortrait spokesperson stills | B |
| 5 | Add `boundary` to every row; one catalog; the R4 test | B |
| 6 | Verify Pages exposure of `atelier/**` source; add exclude or make publication deliberate | M |
| 7 | `THIRD_PARTY_NOTICES.md` + SPDX headers + `PROVENANCE.md` | M |
| 8 | Flag/forbid the AGPL-in-process rows (ultralytics, minio, nebula-nodes, new-api) and the output-reaching model licenses (XTTS-v2, fish-speech) | M |
| 9 | Provenance metadata in `write_bytes()`; demo SVG labelled honestly | M |
| 10 | `pyproject.toml` so the package (and its license) has a real boundary | M |
| 11 | Resolve `integrations/ADAPTERS.md` "Check license" TODO; correct the tldraw hobby-license and Remotion end-user nuances | m |
| 12 | Drop "Lovart-class" from taglines; "OpenAI API" not "ChatGPT API" | m |
| 13 | Extraction trigger recorded (first external contributor / first release artifact / first hosted deploy) | m |

### Explicitly not recommended for v1

- Do not relicense to AGPL to "match" the ecosystem. It would make the ComfyUI-style
  process boundary pointless and poison commercial adoption.
- Do not vendor konva/fabric UMD yet. The sanctioned escape hatch is fine, but it starts
  the notices obligation for no current benefit; the vanilla renderer has not failed yet.
- Do not buy a tldraw or Remotion license to unblock v1. Both are post-v1 by the roadmap;
  the generic contract is the cheaper move.
- Do not write custom legal text unreviewed. Everything in §3, §7, §9 is a first draft to
  put in front of a lawyer — the point is that today there is nothing to review.

---

## 11. Verification log (2026-08-21, primary sources)

| Claim | Status |
|---|---|
| tldraw SDK requires a license key in production since 4.0; hobby = non-commercial + watermark, discretionary; commercial = negotiated value-based pricing; 100-day trial | **confirmed** (tldraw.dev license, license-key and pricing docs) — repo's "watermark for hobby" framing is incomplete |
| Remotion free for individuals / non-profits / for-profit ≤3 people; 4+ needs Company License; Creators $25/seat/mo, Automators $0.01/render with $100/mo min, Enterprise from $500/mo | **confirmed** (remotion.dev license terms + FAQ + LICENSE.md) |
| Remotion: end users of a web app built on Remotion are not Users and do not count toward the threshold | **confirmed** — refines `FUTURE.md`'s reasoning; conclusion still holds for a locally-installed app |
| Open WebUI: BSD-3 + branding clause from v0.6.6 (19 Apr 2025); exemptions ≤50 end users/rolling 30 days, written permission, or enterprise license; ≤v0.6.5 remains plain BSD-3; GitHub reports NOASSERTION | **confirmed** (LICENSE clause 4, docs.openwebui.com) |
| Ultralytics AGPL-3.0: Enterprise License required for SaaS/API/internal/proprietary use; AGPL compliance requires publicly publishing the whole derivative work; fine-tuned weights treated as derivative | **confirmed** (ultralytics.com/license, maintainer statements on issues #22640, #22458) |
| XTTS-v2 weights under CPML — non-commercial only, covering the model **and its outputs**; Coqui Inc. dissolved Jan 2024 so no commercial license is obtainable; toolkit code remains MPL-2.0 | **confirmed** (CPML 1.0.0 text on HF; `coqui-ai/TTS` discussion #4304) |
| simple-icons CC0 covers the SVG files, not the brands' trademarks; project disclaims liability and directs users to per-brand guidelines | **confirmed** (simple-icons DISCLAIMER.md) |
| EU AI Act Art. 50 applies from 2 Aug 2026; provider marking/detection duty has a transition to 2 Dec 2026 only for systems already on the EEA market; penalties up to €15M or 3% turnover; voluntary Code of Practice offers a conformity path | **confirmed** (EC transparency guidelines + quick facts; Cooley and Morgan Lewis analyses, Aug 2026) |
| Gemini API Unpaid Services: Google uses submitted content and generated responses to improve products and ML, with human review; Paid Services excluded | **confirmed** (ai.google.dev/gemini-api/terms) |
| Gemini API **text** output carries no SynthID or machine-readable provenance; image/video do; text watermarking not planned for the API | **confirmed** (Google AI developer forum, staff answer) |
| ComfyUI GPL-3.0, A1111 AGPL-3.0, Fooocus GPL-3.0, ffmpeg LGPL-2.1+/GPL-by-build, penpot MPL-2.0, satori MPL-2.0, Phoenix ELv2, n8n SUL-1.0, Dify Apache+conditions | consistent with the repo's live catalog; the process/subprocess boundary reasoning in `ADAPTERS.md` and `FUTURE.md` is sound |

Re-verify before any release; tldraw, Open WebUI and Remotion have each changed licenses
before, and two of them within the last 18 months.
