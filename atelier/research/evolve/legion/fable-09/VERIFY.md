# Fable-09 · R17 CI — awaiting live agent

Live leftovers now in the tree:

- `.github/workflows/atelier.yml` has two jobs: release gate + evolve legion
- Triggers include `atelier/**`, `pyproject.toml`, and the workflow file
- No live-key smoke job (no secrets)

Verifier: one blocking `claude-fable-5-thinking-high` agent. Do not start
R18 until this note is replaced with the agent's own evidence.
