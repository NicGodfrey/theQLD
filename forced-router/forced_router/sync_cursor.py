from __future__ import annotations

import re
from pathlib import Path

from .config import ForcedModelConfig

_FRONTMATTER_MODEL = re.compile(r"^model:\s*.+$", re.MULTILINE)

AGENT_TEMPLATES: dict[str, str] = {
    "forced-coder.md": """---
name: forced-coder
description: Implementation agent pinned to this repo's specified model. Use for all coding work.
model: {subagent_model}
---

You are the project implementation agent. Stay on the pinned model. Do not switch to Auto.
""",
    "forced-reviewer.md": """---
name: forced-reviewer
description: Review agent pinned to this repo's specified model. Use for code review and verification.
model: {subagent_model}
readonly: true
---

You are the project review agent. Stay on the pinned model. Do not switch to Auto.
""",
}


def sync_cursor_files(cfg: ForcedModelConfig) -> list[Path]:
    agents_dir = cfg.source_path.parent / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    changed: list[Path] = []
    for filename, template in AGENT_TEMPLATES.items():
        path = agents_dir / filename
        rendered = template.format(subagent_model=cfg.spec.subagent_model)
        previous = path.read_text(encoding="utf-8") if path.exists() else ""
        if previous != rendered:
            path.write_text(rendered, encoding="utf-8")
            changed.append(path)
        elif path.exists():
            updated = _FRONTMATTER_MODEL.sub(f"model: {cfg.spec.subagent_model}", previous, count=1)
            if updated != previous:
                path.write_text(updated, encoding="utf-8")
                changed.append(path)
    return changed
