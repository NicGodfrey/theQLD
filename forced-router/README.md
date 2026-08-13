# Forced Auto → specified model

Cursor **Auto / Cursor Router cannot be pinned** to a model you name. Routing is server-side and not configurable per request. This repo does the strongest thing a GitHub project *can* do:

1. **Block Auto in the IDE** (project hooks) unless the picker is already on the specified model.
2. **Pin custom subagents** to that model.
3. **Rewrite** `auto` / `auto-smart` / `default` (and, by default, every other model id) to the specified model for CLI, OpenAI-shaped, Anthropic-shaped, and Cloud Agents API payloads.

Change the model in **one file**: `.cursor/forced-model.json` → `specified_model`.

| Value | Forced model |
| --- | --- |
| `fable5` (default) | Claude Fable 5 Extra High |
| `sol` | GPT-5.6 Sol Extra High |
| `opus5` | Claude Opus 5 High |
| any catalog id string | that id |
| object `{ "id": "..." }` | custom spec |

Then run:

```bash
cd forced-router
PYTHONPATH=. python3 -m forced_router --root .. sync
```

## What this does *not* do

It does not MITM Cursor’s TLS or hijack `api2.cursor.sh`. Desktop Auto still routes on Cursor’s servers if you keep Auto selected; the hook **refuses to send** those prompts so you have to pick the specified model instead.

GitHub `@cursor` issue/PR comments have **no documented `model=` syntax**. Set **Cloud Agents → Default model** at [cursor.com/dashboard/cloud-agents](https://cursor.com/dashboard/cloud-agents) to the same model.

## Quick start

```bash
cd forced-router
PYTHONPATH=. python3 -m unittest discover -s tests -v

# Show the specified model
PYTHONPATH=. python3 -m forced_router --root .. print-model

# Prove Auto is rewritten
PYTHONPATH=. python3 -m forced_router --root .. rewrite '{"model":"auto"}'

# Local rewrite server (optional OpenAI/Anthropic/Cloud Agent facade)
PYTHONPATH=. python3 -m forced_router --root .. serve --port 8788

# Cursor CLI: always injects --model <specified>
PYTHONPATH=. python3 -m forced_router --root .. agent -- -p "hello"
```

Rewrite server:

- `POST /v1/chat/completions` — OpenAI shape, `model: auto` → specified
- `POST /v1/messages` — Anthropic shape
- `POST /v1/agents` — Cloud Agents create body, injects `model.id` + params
- `GET /v1/models` — specified model plus Auto aliases that map to it

Set `UPSTREAM_BASE_URL` (or `--upstream`) to proxy after rewrite. Without it, the server echoes the rewritten model so you can test the force path.

## Repo files

| Path | Role |
| --- | --- |
| `.cursor/forced-model.json` | Specified model + Auto aliases + policy |
| `.cursor/hooks.json` | `beforeSubmitPrompt` + `subagentStart`, `failClosed: true` |
| `.cursor/hooks/force_model.py` | Blocks Auto / wrong models |
| `.cursor/agents/forced-coder.md` | Pinned implementation subagent |
| `.cursor/agents/forced-reviewer.md` | Pinned review subagent |
| `.cursor/rules/forced-model.mdc` | Always-on instruction (does not change the router) |

Policy knobs in `forced-model.json`:

- `block_auto_in_ide` — refuse Auto in the picker
- `block_other_models_in_ide` — refuse anything except the specified model
- `deny_mismatched_subagents` — custom Task subagents must be pinned (Explore/Bash/Browser allowed)
- `force_all_api_models` — rewrite every API model id, not only Auto aliases
- `allow_when_model_missing` — do not brick Cursor if a hook payload omits `model`

## Cloud Agents / GitHub Actions

```bash
agent -p "your task" --model "$(PYTHONPATH=forced-router python3 -m forced_router --root . print-model | python3 -c 'import json,sys; print(json.load(sys.stdin)["cli_model"])')"
```

The workflow `.github/workflows/forced-model.yml` runs the unit tests on every push/PR so the force path cannot regress.
