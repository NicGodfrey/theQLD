# Session Gateway — GPT5.6 sol pool (Option B)

Product-style gateway in front of a **10-slot hot pool** of Cloud Agents named **GPT5.6 sol**, model `gpt-5.6-sol-xhigh`.

Orchestrator (this instance):  
https://cursor.com/agents/bc-4c8e891e-d046-4919-a55a-eafe1e62dcea

## What it enforces

1. **Remote invoke via gateway** — clients never pick a raw worker URL themselves for production traffic.
2. **One session → one worker** — lease is exclusive; a second acquire for the same `clientId` is rejected.
3. **Disconnect ⇒ hard reset** — heartbeat TTL expiry (or explicit release) archives/deletes the old agent and creates a fresh worker in that slot.
4. **Precise billing + full retention** — every turn stores user/assistant/thinking/tool events (sha256) and settles tokens via `GET /v1/agents/{id}/usage`.

## Quick start

```bash
cd session-gateway
cp .env.example .env
# set CURSOR_API_KEY (Dashboard → API Keys) and GATEWAY_API_KEY
npm install
npm run hot-start    # create/fill 10 workers
npm start            # listen on :8787
```

## Client flow

```bash
# 1) acquire
curl -s localhost:8787/v1/session/acquire \
  -H "x-api-key: $GATEWAY_API_KEY" \
  -H 'content-type: application/json' \
  -d '{"clientId":"client-A"}'

# 2) heartbeat every ~15s (TTL default 45s)
curl -s localhost:8787/v1/session/$SESSION_ID/heartbeat \
  -H "x-api-key: $GATEWAY_API_KEY" -X POST

# 3) chat (streams thinking server-side into data/)
curl -s localhost:8787/v1/session/$SESSION_ID/chat \
  -H "x-api-key: $GATEWAY_API_KEY" \
  -H 'content-type: application/json' \
  -d '{"message":"你好，介绍一下你自己"}'

# 4) release → hard reset worker
curl -s localhost:8787/v1/session/$SESSION_ID/release \
  -H "x-api-key: $GATEWAY_API_KEY" \
  -H 'content-type: application/json' \
  -d '{"reason":"client_done"}'
```

## Data layout

| Path | Purpose |
|---|---|
| `data/pool-registry.json` | slot → bcId/url registry |
| `data/gateway.db.json` | leases, turns, billing |
| `data/transcripts/<session>/<turn>/` | full artifact JSON |
| `data/thinking/<session>.ndjson` | append-only reasoning stream |

## Register Task-bootstrapped workers

If workers were created from the orchestrator via Cursor Task(cloud) before `CURSOR_API_KEY` was available:

```bash
npx tsx scripts/register-task-workers.ts workers.json
```

## Notes

- Cursor Agent URLs require auth + repo access; the gateway is the external integration surface.
- Usage API is **token-precise**. USD estimates use optional `USD_PER_MILLION_*` env knobs until you map your plan rates.
- Hard reset is intentional: product cloud agents resume by default; this gateway opts into disposable sessions.
