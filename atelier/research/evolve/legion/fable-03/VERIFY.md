# Fable-03 · R5 upload (conductor fill — agent slot full)

**Pass.** `POST /api/projects/:id/upload` accepts JSON `{filename, mime, data}` base64, 5 MB cap, writes artifact `kind=upload` + board node. Dock drop handler in `web/app.js` calls the same route.

## Remaining
- No multipart/form-data.
- Uploaded image is not automatically attached as vision context on the next weave (spot-edit uses `parent_artifact_id` of generated arts).
- `filePick` input exists hidden but has no click binding.
