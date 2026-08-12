from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from pathlib import Path


def count_tokens(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, (len(stripped) + 3) // 4)


async def stream_reply(prompt: str, sandbox: Path) -> AsyncIterator[dict]:
    """Deterministic fake GPT5.6 sol used for the 10-slot prototype."""
    action, output_text = _handle_tools(prompt, sandbox)
    reasoning = (
        f"槽位沙箱={sandbox.name}。动作={action}。"
        f"按最高智能模式分析输入后给出确定性回复。"
    )
    for chunk in _chunks(reasoning, 24):
        yield {"type": "response.reasoning.delta", "delta": chunk}
        await asyncio.sleep(0)
    for chunk in _chunks(output_text, 20):
        yield {"type": "response.output_text.delta", "delta": chunk}
        await asyncio.sleep(0)
    yield {
        "type": "response.completed",
        "status": "completed",
        "usage": {
            "input_tokens": count_tokens(prompt),
            "cached_input_tokens": 0,
            "visible_output_tokens": count_tokens(output_text),
            "reasoning_tokens": count_tokens(reasoning),
        },
    }


def _chunks(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)] or [""]


def _handle_tools(prompt: str, sandbox: Path) -> tuple[str, str]:
    sandbox.mkdir(parents=True, exist_ok=True)
    note = sandbox / "note.txt"
    raw = prompt.strip()

    if raw.startswith("WRITE:"):
        body = raw[len("WRITE:") :].strip()
        note.write_text(body, encoding="utf-8")
        return "write_note", f"已写入沙箱 note.txt，长度={len(body)}"

    if raw == "READ_NOTE":
        if not note.exists():
            return "read_note", "沙箱中没有 note.txt"
        return "read_note", note.read_text(encoding="utf-8")

    if raw.startswith("READ_FILE:"):
        target = raw[len("READ_FILE:") :].strip()
        try:
            path = (sandbox / target).resolve()
            path.relative_to(sandbox.resolve())
        except (OSError, ValueError):
            return "read_file_denied", "拒绝读取沙箱外路径"
        if not path.exists() or not path.is_file():
            return "read_file_missing", "文件不存在"
        return "read_file", path.read_text(encoding="utf-8")

    if raw == "SHOW_SANDBOX":
        files = sorted(p.name for p in sandbox.iterdir())
        return "show_sandbox", ",".join(files) if files else "(empty)"

    if raw.startswith("SLOW:"):
        return "slow_echo", raw[len("SLOW:") :].strip() or "slow"

    return "echo", f"[GPT5.6 sol] {raw}"
