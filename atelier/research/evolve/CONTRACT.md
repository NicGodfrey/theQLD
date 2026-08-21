# Live Helix HTTP contract (2026-08-21)

Research Board UI (`research/fable5/06-board-ui`) speaks SSE `/api/chat`.
**Live Atelier does not use `/api/chat`.** Do not swap that UI onto this process.

## Live surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/health` | `{ok, architecture: helix, evolve_rounds: 20}` |
| GET/POST | `/api/keys` | Redacted status; unofficial hosts → 400 |
| POST | `/api/quote` | Quote-before-commit. `priced: false` for unknown models |
| GET/POST | `/api/projects` | |
| GET | `/api/projects/:id/board` | `{nodes, camera}` |
| POST | `/api/projects/:id/camera` | Persist pan/zoom |
| POST | `/api/projects/:id/upload` | JSON `{filename, mime, data}` base64 |
| GET | `/api/projects/:id/export` | Zip of board + artifacts |
| POST | `/api/projects/:id/undo` | Pop last add_node |
| POST | `/api/projects/:id/nodes` | Text layer (`type=text`) |
| POST | `/api/threads/:id/run` | Conductor. `?stream=1` → SSE of `events` then `result` |
| GET | `/api/artifacts/:id?download=1` | Attachment filename uses mime ext |
| GET | `/api/usage` | Ledger + totals |

## Status codes

| Code | When |
|---|---|
| 200/201 | Success (`ok: true` on run) |
| 400 | Invalid JSON / unofficial host |
| 402 | Daily or thread budget would be exceeded |
| 413 | Upload > 5 MB |
| 422 | Paid weave failed (fail-closed; no demo SVG) |
| 404 | Missing project/thread/artifact |

## Non-goals on this contract

- Research-only `/api/chat` SSE board
- Lovart credits, video, 3D, PSD, teams
- Following HTTP redirects on credentialed spoke calls
