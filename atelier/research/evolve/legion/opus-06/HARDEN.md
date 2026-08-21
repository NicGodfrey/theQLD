# Opus-06 · R12 text layer — awaiting live agent

Live leftovers now in the tree:

- `POST /api/projects/:id/nodes` `type=text` still has no artifact_id.
- `#textLayer` accepts `Headline · 32` and stores `meta.font_size`.
- The board applies `font_size` / `font_family` / `letter_spacing` as CSS,
  not as pixels in an image.

Verifier: one blocking `claude-opus-5-thinking-high-fast` agent. Do not start
R13 until this note is replaced with the agent's own evidence.
