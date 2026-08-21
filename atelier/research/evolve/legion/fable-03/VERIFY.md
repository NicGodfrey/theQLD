# Fable-03 · R5 upload — awaiting live agent

Live leftovers now in the tree:

- `#uploadBtn` clicks hidden `#filePick`; `change` uploads JSON base64.
- Board drop and keyboard `U` also upload.
- `state.lastUploadId` is sent as `parent_artifact_id` on the next weave
  (spot-edit keywords still prefer `lastArtifactId`).

Verifier: one blocking `claude-fable-5-thinking-high` agent. Do not start R6
until this note is replaced with the agent's own evidence.
