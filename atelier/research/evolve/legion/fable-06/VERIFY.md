# Fable-06 · R11 spot-edit — awaiting live agent

Live leftovers now in the tree:

- Click a board card (or "Use as reference") sets `state.selectedArtifactId`.
- The next weave sends that id as `parent_artifact_id` with no magic words.
- Prompt words `refine` / `larger type` / `bigger type` still fall back to
  `lastArtifactId` when nothing is selected.

Verifier: one blocking `claude-fable-5-thinking-high` agent. Do not start R12
until this note is replaced with the agent's own evidence.
