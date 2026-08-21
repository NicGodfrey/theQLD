"""Project export — board JSON + artifact bytes as a zip (stdlib)."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path


def export_project_zip(memory, artifacts_dir, project_id: str) -> bytes:
    project = memory.get_project(project_id)
    if not project:
        raise ValueError("missing project")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "project.json",
            json.dumps(project, ensure_ascii=False, default=str, indent=2),
        )
        zf.writestr(
            "board.json",
            json.dumps(
                {"nodes": memory.list_nodes(project_id), "camera": project.get("camera")},
                ensure_ascii=False,
                default=str,
                indent=2,
            ),
        )
        threads = []
        for thread in memory.list_threads(project_id):
            item = dict(thread)
            item["messages"] = memory.list_messages(thread["id"])
            threads.append(item)
        zf.writestr(
            "threads.json",
            json.dumps(threads, ensure_ascii=False, default=str, indent=2),
        )
        rows = memory.conn.execute(
            "SELECT * FROM artifacts WHERE project_id=?",
            (project_id,),
        ).fetchall()
        manifest = []
        for row in rows:
            art = dict(row)
            manifest.append({k: art[k] for k in art if k != "path"} | {"filename": Path(art.get("path") or "").name})
            path = Path(art["path"]) if art.get("path") else None
            if path and path.exists() and path.is_file():
                zf.write(path, f"artifacts/{path.name}")
        zf.writestr(
            "artifacts.json",
            json.dumps(manifest, ensure_ascii=False, default=str, indent=2),
        )
    return buf.getvalue()
