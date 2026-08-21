"""Conductor — original Helix design agent (fast | thinking).

Not a clone of Lovart MCoT. Phases are brief → score → route → weave → critique → pin.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from . import usage
from .loom import write_bytes
from .spokes import build_spoke
from .spokes.base import SpokeError

PLANNER_SYSTEM = """You are Helix Conductor, Atelier's design director.
Return ONLY compact JSON (no markdown fences) with this shape:
{
  "mode": "fast" | "thinking",
  "intent": "one sentence",
  "score": {"audience": "", "format": "", "constraints": []},
  "route": {"provider": "openai"|"gemini"|"ollama"|"demo", "model": "", "capability": "chat"|"image"},
  "weave": [{"kind": "image"|"note", "prompt": "", "count": 1}],
  "critique": "optional after-action note",
  "notes": "short"
}
Keep weave prompts concrete and production-oriented. Do not invent APIs.
If the user asked for a board of several assets, emit multiple weave items (max 4).
"""

CRITIC_SYSTEM = """You are Helix Critic. Given a brief and what was produced, return 2-4 sentences:
what works, what to change next, no fluff. Plain text only.
"""


def extract_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise ValueError("conductor plan was not JSON")
    return json.loads(match.group(0))


def fallback_plan(prompt: str, mode: str, provider: str, model: str) -> dict:
    capability = "image"
    return {
        "mode": mode,
        "intent": prompt[:240],
        "score": {
            "audience": "general",
            "format": "single-visual",
            "constraints": ["keep type readable", "no extra logos"],
        },
        "route": {"provider": provider, "model": model, "capability": capability},
        "weave": [{"kind": "image", "prompt": prompt, "count": 1}],
        "critique": "",
        "notes": "local fallback plan",
    }


def next_board_offset(existing_count: int) -> tuple[float, float]:
    col = existing_count % 3
    row = existing_count // 3
    return 72 + col * 360, 72 + row * 280


class Conductor:
    def __init__(self, memory, keyring, artifacts_dir):
        self.memory = memory
        self.keyring = keyring
        self.artifacts_dir = artifacts_dir

    def run(
        self,
        *,
        project_id: str,
        thread_id: str,
        prompt: str,
        mode: str = "fast",
        provider: str = "demo",
        model: str = "",
    ) -> dict:
        mode = "thinking" if mode == "thinking" else "fast"
        provider = (provider or "demo").lower()
        model = model or _default_model(provider, mode)
        brand = (self.memory.get_project(project_id) or {}).get("brand_kit") or {}
        self.memory.add_message(thread_id, "user", prompt)

        spoke = build_spoke(provider, self.keyring)
        plan = fallback_plan(prompt, mode, provider, model)
        planner_messages = [
            {"role": "system", "content": PLANNER_SYSTEM + _brand_block(brand)},
            {
                "role": "user",
                "content": f"Mode={mode}. Preferred provider={provider} model={model}.\nBrief:\n{prompt}",
            },
        ]
        try:
            chat = spoke.chat(planner_messages, model=model if provider != "demo" else "demo-conductor")
            usage.record(
                self.memory,
                provider=chat.provider,
                model=chat.model,
                unit_kind="tokens_in",
                units=chat.tokens_in,
                thread_id=thread_id,
            )
            usage.record(
                self.memory,
                provider=chat.provider,
                model=chat.model,
                unit_kind="tokens_out",
                units=chat.tokens_out,
                thread_id=thread_id,
            )
            parsed = extract_json(chat.text)
            plan.update(parsed)
        except (SpokeError, ValueError, json.JSONDecodeError):
            if provider != "demo":
                # Still produce a local weave so the canvas is never empty.
                pass

        plan["mode"] = mode
        plan.setdefault("route", {})
        plan["route"].setdefault("provider", provider)
        weave_items = plan.get("weave") or [{"kind": "image", "prompt": prompt, "count": 1}]
        artifacts = []
        nodes = []
        existing = len(self.memory.list_nodes(project_id))

        for item in weave_items[:4]:
            kind = item.get("kind") or "image"
            item_prompt = item.get("prompt") or prompt
            count = max(1, min(int(item.get("count") or 1), 2))
            for _ in range(count):
                if kind == "note":
                    node = self.memory.add_node(
                        project_id=project_id,
                        type="note",
                        text=item_prompt,
                        x=next_board_offset(existing)[0],
                        y=next_board_offset(existing)[1],
                        w=280,
                        h=160,
                    )
                    existing += 1
                    nodes.append(node)
                    continue
                image_model = _image_model(plan["route"].get("provider") or provider)
                try:
                    image_spoke = build_spoke(plan["route"].get("provider") or provider, self.keyring)
                    woven = image_spoke.image(item_prompt, model=image_model)
                except SpokeError:
                    image_spoke = build_spoke("demo", self.keyring)
                    woven = image_spoke.image(item_prompt, model="demo-svg")
                art = self.memory.add_artifact(
                    project_id=project_id,
                    thread_id=thread_id,
                    kind="image",
                    mime=woven.mime,
                    prompt=item_prompt,
                    provider=woven.provider,
                    model=woven.model,
                )
                path = write_bytes(self.artifacts_dir, art["id"], woven.data, woven.mime)
                self.memory.conn.execute("UPDATE artifacts SET path=? WHERE id=?", (str(path), art["id"]))
                self.memory.conn.commit()
                art["path"] = str(path)
                usage.record(
                    self.memory,
                    provider=woven.provider,
                    model=woven.model,
                    unit_kind="images",
                    units=1,
                    thread_id=thread_id,
                )
                x, y = next_board_offset(existing)
                node = self.memory.add_node(
                    project_id=project_id,
                    type="image",
                    artifact_id=art["id"],
                    text=item_prompt,
                    x=x,
                    y=y,
                )
                existing += 1
                artifacts.append(art)
                nodes.append(node)

        critique = ""
        if mode == "thinking":
            try:
                critic = spoke.chat(
                    [
                        {"role": "system", "content": CRITIC_SYSTEM},
                        {
                            "role": "user",
                            "content": f"Brief: {prompt}\nPlan: {json.dumps(plan)[:1500]}\nArtifacts: {len(artifacts)}",
                        },
                    ],
                    model=model if provider != "demo" else "demo-conductor",
                )
                critique = critic.text.strip()
                usage.record(
                    self.memory,
                    provider=critic.provider,
                    model=critic.model,
                    unit_kind="tokens_out",
                    units=critic.tokens_out,
                    thread_id=thread_id,
                )
            except SpokeError:
                critique = "Thinking pass stored the plan; critic skipped (provider unavailable)."
            plan["critique"] = critique

        summary = _summarize(plan, artifacts, critique)
        self.memory.add_message(thread_id, "assistant", summary, plan=plan)
        if plan.get("intent") and not (self.memory.get_thread(thread_id) or {}).get("topic"):
            self.memory.conn.execute(
                "UPDATE threads SET topic=?, mode=? WHERE id=?",
                (plan["intent"][:80], mode, thread_id),
            )
            self.memory.conn.commit()

        return {
            "plan": plan,
            "artifacts": artifacts,
            "nodes": nodes,
            "message": summary,
        }


def _default_model(provider: str, mode: str) -> str:
    if provider == "openai":
        return "gpt-4o-mini"
    if provider == "gemini":
        return "gemini-2.0-flash"
    if provider == "ollama":
        return "llama3.2"
    return "demo-conductor"


def _image_model(provider: str) -> str:
    if provider == "openai":
        return "dall-e-3"
    if provider == "gemini":
        return "gemini-2.0-flash-preview-image-generation"
    return "demo-svg"


def _brand_block(brand: dict) -> str:
    if not brand:
        return ""
    return "\nBrand kit JSON (must obey): " + json.dumps(brand, ensure_ascii=False)[:1200]


def _summarize(plan: dict, artifacts: list[dict], critique: str) -> str:
    lines = [
        f"Helix {plan.get('mode', 'fast')} · {plan.get('intent') or 'brief received'}",
        f"Route: {(plan.get('route') or {}).get('provider')} / {(plan.get('route') or {}).get('model')}",
        f"Pinned {len(artifacts)} artifact(s) onto the board.",
    ]
    if critique:
        lines.append("Critique: " + critique)
    elif plan.get("notes"):
        lines.append(str(plan["notes"]))
    return "\n".join(lines)
