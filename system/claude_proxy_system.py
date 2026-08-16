#!/usr/bin/env python3
"""Anthropic Messages API `system` blocks built from the repo's prompt pack."""

from load_system import MODEL, PROMPT_FILES, PROMPTS_DIR


def build_system_blocks() -> list:
    blocks = []
    for name in PROMPT_FILES:
        text = (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()
        blocks.append({"type": "text", "text": text})
    return blocks


def build_request(messages: list, model: str = MODEL, max_tokens: int = 4096) -> dict:
    return {
        "model": model,
        "max_tokens": max_tokens,
        "system": build_system_blocks(),
        "messages": messages,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(build_request(messages=[]), ensure_ascii=False, indent=2))
