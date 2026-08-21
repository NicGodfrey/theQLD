# 20-round self-test / self-evolution

Odd rounds are Fable-shaped (expose a gap with a test). Even rounds are Opus-shaped (smallest live fix). The parent conductor implemented the live path; a 10+10 fast legion verifies each slice under `legion/`.

| Round | Theme | Live change |
|---|---|---|
| 1 | Fail-closed | Paid `SpokeError` no longer mints demo SVG |
| 2 | Quote | `POST /api/quote` + quote attached to plan |
| 3 | Progress | `run.events` phases; `?stream=1` SSE |
| 4 | Download | `?download=1` brief slug; CSP on SVG; nosniff on export |
| 5 | Upload | JSON upload + `#filePick` + last upload as weave parent |
| 6 | Camera | Persist + clamp; Home / Fit; debounced write |
| 7 | Plan card | Plan stored on assistant message; dock card |
| 8 | 4-up | `variants=4` / “four variants” → 2×2 |
| 9 | Undo | `undo_log` + `POST .../undo` |
| 10 | Brand kit | Demo SVG + planner consume palette |
| 11 | Spot-edit | `parent_artifact_id` on the next weave |
| 12 | Text layer | `type=text` nodes, not baked into raster |
| 13 | Export | `GET .../export` zip |
| 14 | Launcher | `atelier/__main__.py` bootstraps repo root |
| 15 | Host pin | Keyring rejects unofficial hosts; spokes refuse redirects |
| 16 | Budget 402 | Pre-call quote + HTTP 402 |
| 17 | CI | `.github/workflows/atelier.yml` |
| 18 | Contract | This tree’s `CONTRACT.md` (live ≠ research `/api/chat`) |
| 19 | Eval | `atelier/data/eval/*.json` |
| 20 | Scorecard | `SCORECARD.json` gate ≥ 16/20 |

Release gate:

```bash
python3 -m unittest atelier.tests.test_helix atelier.tests.test_evolve
```
