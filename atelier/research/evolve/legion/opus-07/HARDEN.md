# Opus-07 · R14 launcher — awaiting live agent

Live leftovers now in the tree:

- `pyproject.toml` console script `atelier = atelier.launch:main`
- `atelier --help` / `python3 -m atelier --help` print flags and do not bind
- `--host` / `--port` override `ATELIER_HOST` / `ATELIER_PORT`
- `__main__.py` still inserts repo root on `sys.path` so an absolute path works

Verifier: one blocking `claude-opus-5-thinking-high-fast` agent. Do not start
R15 until this note is replaced with the agent's own evidence.
