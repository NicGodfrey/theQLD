#!/usr/bin/env python3
"""Build the Claude system prompt from the repo's prompt pack (stdlib only)."""

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"

# Order matters: identity first, then access path, then operating rules, then main prompt.
PROMPT_FILES = (
    "identity.md",
    "proxy.md",
    "claude-code-prefix.md",
    "system.md",
)

MODEL = "claude-fable-5"


def load_system_prompt() -> str:
    parts = []
    for name in PROMPT_FILES:
        path = PROMPTS_DIR / name
        parts.append(path.read_text(encoding="utf-8").strip())
    return "\n\n---\n\n".join(parts) + "\n"


def build_payload() -> dict:
    return {"model": MODEL, "system": load_system_prompt(), "messages": []}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--print", action="store_true", dest="print_",
                       help="write the concatenated system prompt to stdout (default)")
    group.add_argument("--json", action="store_true",
                       help="write a Messages API-shaped JSON payload to stdout")
    args = parser.parse_args()

    if args.json:
        print(json.dumps(build_payload(), ensure_ascii=False, indent=2))
    else:
        print(load_system_prompt(), end="")


if __name__ == "__main__":
    main()
