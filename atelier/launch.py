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

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MIN_PORT = 1
MAX_PORT = 65535


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def repo_root() -> Path:
    return package_dir().parent


def ensure_sys_path() -> Path:
    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


def port_number(raw) -> int:
    """argparse `type=` for a bindable port. 0 is refused: the banner and the
    Host guard both need the port the user asked for."""
    try:
        port = int(str(raw).strip())
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"{raw!r} is not a number") from None
    if not MIN_PORT <= port <= MAX_PORT:
        raise argparse.ArgumentTypeError(f"{port} is outside {MIN_PORT}-{MAX_PORT}")
    return port


def env_host(environ=None) -> str | None:
    """ATELIER_HOST, or None when unset or blank. A blank value would bind
    every interface *and* switch off the Host guard, which nobody asks for."""
    raw = (os.environ if environ is None else environ).get("ATELIER_HOST")
    if raw is None:
        return None
    return raw.strip() or None


def env_port(environ=None) -> int | None:
    """ATELIER_PORT, or None when unset or unusable. Junk must not stop
    `atelier --help` from printing."""
    raw = (os.environ if environ is None else environ).get("ATELIER_PORT")
    if raw is None:
        return None
    try:
        return port_number(raw)
    except argparse.ArgumentTypeError:
        return None


def env_warnings(environ=None) -> list[str]:
    env = os.environ if environ is None else environ
    notes = []
    raw_host = env.get("ATELIER_HOST")
    if raw_host is not None and env_host(env) is None:
        notes.append(f"atelier: ATELIER_HOST is blank — binding {DEFAULT_HOST}")
    raw_port = env.get("ATELIER_PORT")
    if raw_port is not None and env_port(env) is None:
        notes.append(
            f"atelier: ATELIER_PORT={raw_port!r} is not a port in "
            f"{MIN_PORT}-{MAX_PORT} — using {DEFAULT_PORT}"
        )
    return notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atelier",
        description="Atelier Helix — local BYOK design studio (stdlib, official hosts only).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=env_host() or DEFAULT_HOST,
        help=f"Bind address (default {DEFAULT_HOST}, or ATELIER_HOST).",
    )
    parser.add_argument(
        "--port",
        type=port_number,
        default=env_port() or DEFAULT_PORT,
        help=f"Bind port (default {DEFAULT_PORT}, or ATELIER_PORT).",
    )
    return parser


def parse_args(argv=None):
    args = build_parser().parse_args(argv)
    args.host = (args.host or "").strip() or DEFAULT_HOST
    return args


def main(argv=None) -> None:
    ensure_sys_path()
    args = parse_args(argv)
    for note in env_warnings():
        print(note, file=sys.stderr, flush=True)
    from atelier.server import main as serve

    serve(host=args.host, port=args.port)
