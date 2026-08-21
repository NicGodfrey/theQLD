# Opus-07 · R14 launcher (conductor fill — agent slot full)

**Pass.** `atelier/__main__.py` inserts repo root on `sys.path` before import. `atelier/launch.py` `repo_root()` / `ensure_sys_path()` let `python3 /abs/path/atelier/__main__.py` start from any cwd. Web assets resolve via `Path(__file__)`.

## Remaining
- No `pyproject.toml` console_script.
- `python3 -m atelier` still needs the package on `PYTHONPATH` (repo root or installed).
