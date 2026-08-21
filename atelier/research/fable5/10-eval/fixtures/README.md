# Fixtures — sample briefs for the Atelier Helix eval harness

Four briefs exercise the four launch scenarios. Each file is one JSON object:

| field      | meaning                                                                 |
|------------|-------------------------------------------------------------------------|
| `id`       | short handle used in test names and the eval scorecard                  |
| `title`    | human label                                                             |
| `request`  | the raw creative request, exactly as a user would type it into Helix    |
| `brand`    | (optional) brand kit context: name, palette, fonts                      |
| `data`     | (optional) structured content the layout must consume (fact-sheet entries) |
| `assets`   | (optional) assets the brief refers to (brand-kit apply)                 |
| `expected` | machine-checkable expectations used by `test_helix.py` and `--eval`     |

## The `expected` block

| key                  | checked by                                                        |
|----------------------|-------------------------------------------------------------------|
| `task_type`          | eval scorecard label only (plans carry no task_type field)         |
| `crafts_required`    | every one of these crafts must appear among the plan's steps       |
| `crafts_any_of`      | at least one of these must appear (empty list = no constraint)     |
| `lanes_required`     | after routing, these lanes must be used                            |
| `lanes_forbidden`    | after routing, none of these lanes may appear (video/audio/3d)     |
| `min_steps`          | lower bound on plan size                                           |
| `handoff_min`        | lower bound on client-facing handoff artifacts                     |
| `deliverable_kinds`  | artifact kinds (`text`/`json`/`image`) that must reach the manifest |
| `palette`            | hex constraints that must be restated inside step instructions (PROTOCOL.md: "Constraints must be restated inside every instruction they bind") |
| `must_mention`       | names that must survive brief → plan (reading or instructions)     |
| `content_terms`      | (fact sheet only) source-data strings that must appear in woven artifacts — proves content flows through `[[step_id]]` tokens, not just prompts |

## Fixture briefs

1. **`brief_logo.json`** — 'Atelier Helix' double-helix monogram; one-colour mark
   `#1A5FB4`, accent `#F5C211`; mark + style note.
2. **`brief_poster.json`** — A3 exhibition poster for 'Night Loom' at Brisbane
   Powerhouse; dark ground, two neon accents, legible at three metres.
3. **`brief_factsheet_legal_directory.json`** — one-page fact-sheet template for
   The Queensland Legal Directory plus a rendered preview. Carries three real
   directory entries (from `theqld.com/legalDirectory.html`) so the harness can
   verify that entry names and phone numbers flow into the artifacts.
4. **`brief_brand_kit_apply.json`** — restyle an existing launch poster to the
   Atelier Helix kit (palette + Archivo/Inter), composition unchanged, plus a
   change log. Exercises `refine-image` routing.

Briefs are plain text on purpose: the conductor contract (05-conductor/PROTOCOL.md)
starts from a raw request, and the fixtures should not leak plan structure to the
planner.
