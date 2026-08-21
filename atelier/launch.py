"""Cwd-independent Atelier launcher.

`python3 -m atelier` works from the repo root. `atelier` works after
`pip install -e .` via the console script in pyproject.toml. Absolute
`python3 /path/to/atelier/__main__.py` also works from any cwd because
this module puts the repository root on sys.path before importing server.
"""

from __future__ import annotations

import argparse
import os
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atelier",
        description="Atelier Helix — local BYOK design studio (stdlib, official hosts only).",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("ATELIER_HOST", "127.0.0.1"),
        help="Bind address (default 127.0.0.1, or ATELIER_HOST).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("ATELIER_PORT", "8765")),
        help="Bind port (default 8765, or ATELIER_PORT).",
    )
    return parser


def parse_args(argv=None):
    return build_parser().parse_args(argv)


def main(argv=None) -> None:
    ensure_sys_path()
    args = parse_args(argv)
    from atelier.server import main as serve

    serve(host=args.host, port=args.port)
