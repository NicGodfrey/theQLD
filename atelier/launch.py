"""Cwd-independent Atelier launcher.

`python3 -m atelier` works from the repo root. This module also lets
`python3 /abs/path/atelier/__main__.py` work from any working directory
by putting the repository root on sys.path.
"""

from __future__ import annotations

import sys
from pathlib import Path


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    return package_dir().parent


def ensure_sys_path() -> Path:
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def main() -> None:
    ensure_sys_path()
    from atelier.server import main as serve

    serve()
