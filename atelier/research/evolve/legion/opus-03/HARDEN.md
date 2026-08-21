# Opus-03 · R6 camera (conductor fill — agent slot full)

**Pass.** `projects.camera` JSON `{x,y,zoom}` persisted via `POST /api/projects/:id/camera`. Board GET returns camera. Wheel zoom 0.25–3; empty-space pan; node drag divides by zoom.

## Remaining
- No pinch / trackpad-precision pan.
- No fit-to-content or home-view.
- Persist is best-effort (errors swallowed).
