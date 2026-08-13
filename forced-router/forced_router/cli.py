from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .config import dump_public, load_config
from .rewrite import rewrite_cli_argv, rewrite_payload
from .server import serve
from .sync_cursor import sync_cursor_files


def _cfg(ns: argparse.Namespace):
    start = Path(ns.root).resolve() if getattr(ns, "root", None) else None
    return load_config(start)


def cmd_print_model(ns: argparse.Namespace) -> int:
    cfg = _cfg(ns)
    json.dump(dump_public(cfg), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_rewrite(ns: argparse.Namespace) -> int:
    cfg = _cfg(ns)
    payload = json.loads(ns.body)
    if not isinstance(payload, dict):
        raise SystemExit("rewrite body must be a JSON object")
    out = rewrite_payload(payload, cfg, for_api=ns.api)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_serve(ns: argparse.Namespace) -> int:
    cfg = _cfg(ns)
    upstream = ns.upstream or os.environ.get("UPSTREAM_BASE_URL")
    serve(cfg, host=ns.host, port=ns.port, upstream=upstream)
    return 0


def cmd_sync(ns: argparse.Namespace) -> int:
    cfg = _cfg(ns)
    changed = sync_cursor_files(cfg)
    for path in changed:
        print(f"updated {path}")
    if not changed:
        print("already in sync")
    return 0


def cmd_agent(ns: argparse.Namespace) -> int:
    cfg = _cfg(ns)
    extra = list(ns.agent_args or [])
    if extra[:1] == ["--"]:
        extra = extra[1:]
    argv = rewrite_cli_argv(["agent", *extra], cfg)
    print("exec:", " ".join(argv), file=sys.stderr)
    try:
        return subprocess.call(argv)
    except FileNotFoundError:
        print(
            "cursor `agent` CLI not found on PATH. Install it, then rerun.\n"
            f"Equivalent: {' '.join(argv)}",
            file=sys.stderr,
        )
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forced_router",
        description="Force Auto/Router model aliases onto the model in .cursor/forced-model.json",
    )
    parser.add_argument("--root", help="Repo root containing .cursor/forced-model.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("print-model", help="Show the specified model")
    p.set_defaults(func=cmd_print_model)

    p = sub.add_parser("rewrite", help="Rewrite a JSON request body")
    p.add_argument("body", help='JSON object, e.g. \'{"model":"auto"}\'')
    p.add_argument("--api", action="store_true", help="Use API id instead of CLI id")
    p.set_defaults(func=cmd_rewrite)

    p = sub.add_parser("serve", help="OpenAI/Anthropic/Cloud-Agent compatible rewrite server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8788)
    p.add_argument("--upstream", default=None, help="Optional real provider base URL")
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("sync", help="Rewrite .cursor agent frontmatter to the specified model")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("agent", help="Run Cursor CLI `agent` with the specified model forced")
    p.add_argument("agent_args", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_agent)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return int(ns.func(ns))


if __name__ == "__main__":
    raise SystemExit(main())
