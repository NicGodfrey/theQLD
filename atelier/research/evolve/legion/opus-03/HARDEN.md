# Opus-03 · R6 camera — awaiting live agent

Live leftovers now in the tree:

- `POST /api/projects/:id/camera` persists `{x,y,zoom}`; zoom clamped to 0.25–3.
- Home / Fit buttons and click-to-reset on the readout.
- Persist is debounced (180 ms) so wheel zoom does not write every tick.

Verifier: one blocking `claude-opus-5-thinking-high-fast` agent. Do not start
R7 until this note is replaced with the agent's own evidence.
