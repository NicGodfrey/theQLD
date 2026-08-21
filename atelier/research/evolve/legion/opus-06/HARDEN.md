# Opus-06 · R12 text layer (conductor fill — agent slot full)

**Pass.** `POST /api/projects/:id/nodes` with `type=text` creates a node with `meta.layer=text` and no artifact_id. Weave `kind=text` also pins a text node. CSS `.text-layer` is dashed, not a raster.

## Remaining
- No font/size/tracking controls.
- Text is not exported as a separate SVG/PDF layer beyond `board.json`.
