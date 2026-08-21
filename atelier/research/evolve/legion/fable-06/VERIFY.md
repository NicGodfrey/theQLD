# Fable-06 · R11 spot-edit (conductor fill — agent slot full)

**Pass.** `parent_artifact_id` stored on the new artifact; plan.spot_edit set. UI heuristic: prompt matching `/spot|局部|edit this/i` plus `state.lastArtifactId`.

## Remaining
- No box/mask region, no inpainting API fields.
- Heuristic can miss “make the type larger” without the words spot/edit.
