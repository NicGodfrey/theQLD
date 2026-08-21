"""Conductor — original Helix design agent (fast | thinking).

Not a clone of Lovart MCoT. Phases are brief → score → route → weave → critique → pin.

Lanes (see research/fable5/05-conductor/ROUTING.md):
  openai  — structured JSON / copy
  gemini  — multimodal read or long source
  image   — synthesis only

Paid-provider failures are fail-closed: they never silently become demo SVG.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Optional

from . import usage
from .loom import write_bytes
from .quote import as_int, quote_run
from .spokes import KNOWN_PROVIDERS, build_spoke
from .spokes.base import SpokeError

PLANNER_SYSTEM = """You are Helix Conductor, Atelier's design director.
Return ONLY compact JSON (no markdown fences) with this shape:
{
  "mode": "fast" | "thinking",
  "intent": "one sentence",
  "score": {"audience": "", "format": "", "constraints": []},
  "route": {"provider": "openai"|"gemini"|"ollama"|"demo", "model": "", "capability": "chat"|"image"},
  "weave": [{"kind": "image"|"note"|"text", "prompt": "", "count": 1}],
  "critique": "optional after-action note",
  "notes": "short"
}
Keep weave prompts concrete and production-oriented. Do not invent APIs.
If the user asked for a board of several assets, emit multiple weave items (max 4).
"""

CRITIC_SYSTEM = """You are Helix Critic. Given a brief and what was produced, return 2-4 sentences:
what works, what to change next, no fluff. Plain text only.
"""


class ConductorError(RuntimeError):
    def __init__(self, message: str, code: str = "weave_failed"):
        super().__init__(message)
        self.code = code


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


def next_board_offset(existing_count: int, grid: int = 3) -> tuple[float, float]:
    grid = 2 if grid == 2 else 3
    col = existing_count % grid
    row = existing_count // grid
    return 72 + col * 360, 72 + row * 280


def _wants_variants(prompt: str, variants: int) -> int:
    if variants and int(variants) > 1:
        return max(2, min(int(variants), 4))
    low = (prompt or "").lower()
    if any(token in low for token in ("4-up", "four variants", "4 variants", "四宫格", "四个变体")):
        return 4
    if "variants" in low or "变体" in low:
        return 4
    return 0


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
        variants: int = 0,
        parent_artifact_id: Optional[str] = None,
        on_event: Optional[Callable[[dict], None]] = None,
    ) -> dict:
        mode = "thinking" if mode == "thinking" else "fast"
        provider = (provider or "demo").strip().lower()
        model = model or _default_model(provider, mode)
        brand = (self.memory.get_project(project_id) or {}).get("brand_kit") or {}
        palette = brand.get("palette") if isinstance(brand, dict) else None
        # No kit means no lock: never invent a brand name into a paid prompt.
        brand_title = brand.get("name") if isinstance(brand, dict) else None
        events: list[dict] = []

        def emit(kind: str, **payload: Any) -> dict:
            ev = {"kind": kind, **payload}
            events.append(ev)
            if on_event:
                on_event(ev)
            return ev

        emit("phase", phase="brief")

        if provider not in KNOWN_PROVIDERS:
            raise ConductorError(f"Unknown provider {provider!r}", code="unknown_provider")

        q = quote_run(
            provider=provider,
            model=model,
            prompt=prompt,
            count=max(1, _wants_variants(prompt, variants) or 1),
            memory=self.memory,
            thread_id=thread_id,
        )
        emit("quote", quote=q)
        if q.get("would_exceed"):
            raise usage.BudgetExceeded(q.get("reason") or "budget exceeded")

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
        emit("phase", phase="score")
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
        except (SpokeError, ValueError, json.JSONDecodeError) as exc:
            emit("planner_fallback", error=str(exc))
            if provider != "demo" and isinstance(exc, SpokeError) and "key missing" in str(exc).lower():
                raise ConductorError(str(exc), code="auth") from exc

        plan["mode"] = mode
        plan.setdefault("route", {})
        plan["route"]["provider"] = provider
        plan["quote"] = {k: q[k] for k in ("estimated_usd", "priced", "provider", "image_model", "count") if k in q}
        emit("phase", phase="route", route=plan.get("route"))

        weave_items = list(plan.get("weave") or [{"kind": "image", "prompt": prompt, "count": 1}])
        n_variants = _wants_variants(prompt, variants)
        if n_variants >= 2:
            first = weave_items[0] if weave_items else {"kind": "image", "prompt": prompt}
            weave_items = [
                {
                    "kind": "image",
                    "prompt": f"{first.get('prompt') or prompt} — variant {i + 1}",
                    "count": 1,
                }
                for i in range(n_variants)
            ]
            plan["variants"] = n_variants

        image_count = 0
        for item in weave_items[:4]:
            kind = item.get("kind") or "image"
            if kind not in {"note", "text"}:
                image_count += as_int(item.get("count"), default=1, lo=1, hi=2)
        if image_count and image_count != q.get("count"):
            q = quote_run(
                provider=provider,
                model=model,
                prompt=prompt,
                count=image_count,
                memory=self.memory,
                thread_id=thread_id,
            )
            emit("quote", quote=q)
            if q.get("would_exceed"):
                raise usage.BudgetExceeded(q.get("reason") or "budget exceeded")
            plan["quote"] = {
                k: q[k] for k in ("estimated_usd", "priced", "provider", "image_model", "count") if k in q
            }
        parent = None
        if parent_artifact_id:
            parent = self.memory.get_artifact(parent_artifact_id)
            if parent:
                plan["spot_edit"] = {"parent_id": parent_artifact_id}
        artifacts = []
        nodes = []
        errors = []
        existing = len(self.memory.list_nodes(project_id))
        grid = 2 if (n_variants >= 2 or len(weave_items) >= 4) else 3
        route_provider = (plan["route"].get("provider") or provider).lower()

        emit("phase", phase="weave")
        for item in weave_items[:4]:
            kind = item.get("kind") or "image"
            item_prompt = item.get("prompt") or prompt
            if parent:
                item_prompt = (
                    f"Spot-edit of previous artifact ({parent.get('id')}). "
                    f"Direction: {prompt}. Original brief: {parent.get('prompt') or ''}. "
                    f"Variant prompt: {item_prompt}"
                )
            count = max(1, min(int(item.get("count") or 1), 2))
            for _ in range(count):
                if kind in {"note", "text"}:
                    x, y = next_board_offset(existing, grid=grid)
                    node = self.memory.add_node(
                        project_id=project_id,
                        type="text" if kind == "text" else "note",
                        text=item_prompt,
                        x=x,
                        y=y,
                        w=280,
                        h=160,
                        meta={"layer": "text"} if kind == "text" else {},
                    )
                    existing += 1
                    nodes.append(node)
                    emit("pin", node_id=node["id"], type=node["type"])
                    continue
                image_model = _image_model(route_provider)
                try:
                    image_spoke = build_spoke(route_provider, self.keyring)
                    woven = image_spoke.image(
                        item_prompt,
                        model=image_model,
                        palette=palette,
                        title=brand_title,
                    )
                except SpokeError as exc:
                    errors.append(str(exc))
                    emit("error", message=str(exc), provider=route_provider)
                    if route_provider != "demo":
                        # Fail closed — never mint a demo SVG that looks like a paid success.
                        continue
                    image_spoke = build_spoke("demo", self.keyring)
                    woven = image_spoke.image(
                        item_prompt,
                        model="demo-svg",
                        palette=palette,
                        title=brand_title,
                    )
                art = self.memory.add_artifact(
                    project_id=project_id,
                    thread_id=thread_id,
                    kind="image",
                    mime=woven.mime,
                    prompt=item_prompt,
                    provider=woven.provider,
                    model=woven.model,
                    parent_id=parent["id"] if parent else None,
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
                x, y = next_board_offset(existing, grid=grid)
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
                emit("pin", artifact_id=art["id"], node_id=node["id"], provider=woven.provider)

        if errors and not artifacts and not any(n.get("type") in {"note", "text"} for n in nodes):
            raise ConductorError(errors[0], code="spoke_error")

        critique = ""
        if mode == "thinking":
            emit("phase", phase="critique")
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

        emit("phase", phase="pin")
        summary = _summarize(plan, artifacts, critique, errors)
        self.memory.add_message(thread_id, "assistant", summary, plan=plan)
        if plan.get("intent") and not (self.memory.get_thread(thread_id) or {}).get("topic"):
            self.memory.conn.execute(
                "UPDATE threads SET topic=?, mode=? WHERE id=?",
                (plan["intent"][:80], mode, thread_id),
            )
            self.memory.conn.commit()

        emit("phase", phase="done")
        return {
            "ok": True,
            "plan": plan,
            "artifacts": artifacts,
            "nodes": nodes,
            "message": summary,
            "events": events,
            "errors": errors,
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
        return "gpt-image-1"
    if provider == "gemini":
        return "gemini-2.5-flash-image"
    return "demo-svg"


def _brand_block(brand: dict) -> str:
    if not brand:
        return ""
    return "\nBrand kit JSON (must obey): " + json.dumps(brand, ensure_ascii=False)[:1200]


def _summarize(plan: dict, artifacts: list[dict], critique: str, errors: list[str]) -> str:
    lines = [
        f"Helix {plan.get('mode', 'fast')} · {plan.get('intent') or 'brief received'}",
        f"Route: {(plan.get('route') or {}).get('provider')} / {(plan.get('route') or {}).get('model')}",
        f"Pinned {len(artifacts)} artifact(s) onto the board.",
    ]
    if plan.get("variants"):
        lines.append(f"Variants: {plan['variants']}")
    if plan.get("quote"):
        q = plan["quote"]
        priced = "priced" if q.get("priced") else "unpriced conservative"
        lines.append(f"Quote: ${q.get('estimated_usd', 0):.4f} ({priced})")
    if critique:
        lines.append("Critique: " + critique)
    elif plan.get("notes"):
        lines.append(str(plan["notes"]))
    if errors:
        lines.append("Warnings: " + " | ".join(errors[:3]))
    return "\n".join(lines)
