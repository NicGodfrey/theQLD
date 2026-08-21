"""Helix Memory — SQLite persistence for projects, threads, canvas, artifacts."""

from __future__ import annotations

import json
import math
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    brand_kit TEXT NOT NULL DEFAULT '{}',
    camera TEXT NOT NULL DEFAULT '{"x":0,"y":0,"zoom":1}',
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS threads (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    topic TEXT NOT NULL DEFAULT '',
    mode TEXT NOT NULL DEFAULT 'fast',
    created_at REAL NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    plan_json TEXT,
    created_at REAL NOT NULL,
    FOREIGN KEY (thread_id) REFERENCES threads(id)
);
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    thread_id TEXT,
    kind TEXT NOT NULL,
    path TEXT NOT NULL DEFAULT '',
    mime TEXT NOT NULL DEFAULT 'image/svg+xml',
    prompt TEXT NOT NULL DEFAULT '',
    provider TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    parent_id TEXT,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    type TEXT NOT NULL,
    x REAL NOT NULL DEFAULT 80,
    y REAL NOT NULL DEFAULT 80,
    w REAL NOT NULL DEFAULT 320,
    h REAL NOT NULL DEFAULT 240,
    z INTEGER NOT NULL DEFAULT 0,
    artifact_id TEXT,
    text TEXT NOT NULL DEFAULT '',
    meta TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS usage_events (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    unit_kind TEXT NOT NULL,
    units REAL NOT NULL,
    estimated_usd REAL NOT NULL DEFAULT 0,
    thread_id TEXT,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS undo_log (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    action TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""


def _now() -> float:
    return time.time()


def _id() -> str:
    return uuid.uuid4().hex


def _finite(value: Any, default: Optional[float]) -> Optional[float]:
    """A real number for a NOT NULL REAL column, or `default`.

    A JSON `null` or a NaN both land as NULL and raise IntegrityError mid-write;
    an Infinity survives the insert and then serialises as a bare `Infinity`
    token, which is not JSON — one such node makes every later /board response
    unparseable in the browser.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return default
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


class Memory:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript(SCHEMA)
        self._migrate()
        self.conn.commit()

    def _migrate(self) -> None:
        pcols = {r[1] for r in self.conn.execute("PRAGMA table_info(projects)")}
        if "camera" not in pcols:
            self.conn.execute(
                "ALTER TABLE projects ADD COLUMN camera TEXT NOT NULL DEFAULT '{\"x\":0,\"y\":0,\"zoom\":1}'"
            )
        acols = {r[1] for r in self.conn.execute("PRAGMA table_info(artifacts)")}
        if "parent_id" not in acols:
            self.conn.execute("ALTER TABLE artifacts ADD COLUMN parent_id TEXT")

    def close(self) -> None:
        self.conn.close()

    def _row(self, row: sqlite3.Row | None) -> Optional[dict]:
        return dict(row) if row else None

    def _rows(self, rows: list[sqlite3.Row]) -> list[dict]:
        return [dict(r) for r in rows]

    def create_project(self, name: str, brand_kit: Optional[dict] = None) -> dict:
        pid = _id()
        kit = json.dumps(brand_kit or {}, ensure_ascii=False)
        self.conn.execute(
            "INSERT INTO projects (id, name, brand_kit, created_at) VALUES (?,?,?,?)",
            (pid, name, kit, _now()),
        )
        self.conn.commit()
        return self.get_project(pid)

    def _hydrate_project(self, row: Optional[dict]) -> Optional[dict]:
        if not row:
            return None
        row["brand_kit"] = json.loads(row["brand_kit"] or "{}") if isinstance(row.get("brand_kit"), str) else (row.get("brand_kit") or {})
        row["camera"] = json.loads(row["camera"] or '{"x":0,"y":0,"zoom":1}') if isinstance(row.get("camera"), str) else (row.get("camera") or {"x": 0, "y": 0, "zoom": 1})
        return row

    def list_projects(self) -> list[dict]:
        return [
            self._hydrate_project(dict(r))
            for r in self.conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
        ]

    def get_project(self, project_id: str) -> Optional[dict]:
        row = self._row(
            self.conn.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
        )
        return self._hydrate_project(row)

    def set_camera(self, project_id: str, camera: dict) -> Optional[dict]:
        cam = camera if isinstance(camera, dict) else {}

        def _num(value, default: float) -> float:
            # NaN / ±Infinity round-trip through json.loads but json.dumps writes
            # them as bare tokens, which is not JSON: one such write would make
            # every later /api/projects response unparseable in the browser.
            try:
                out = float(value)
            except (TypeError, ValueError):
                return default
            return out if math.isfinite(out) else default

        if not self.get_project(project_id):
            return None
        zoom = _num(cam.get("zoom"), 1.0)
        if zoom <= 0:
            zoom = 1.0
        payload = {
            "x": _num(cam.get("x"), 0.0),
            "y": _num(cam.get("y"), 0.0),
            "zoom": min(3.0, max(0.25, zoom)),
        }
        self.conn.execute(
            "UPDATE projects SET camera=? WHERE id=?",
            (json.dumps(payload), project_id),
        )
        self.conn.commit()
        return self.get_project(project_id)

    def update_brand_kit(self, project_id: str, brand_kit: dict) -> Optional[dict]:
        from atelier.helix.loom import brand_colors, brand_name

        if not self.get_project(project_id):
            return None
        kit = brand_kit if isinstance(brand_kit, dict) else {}
        cleaned = {
            "name": brand_name(kit.get("name")),
            "palette": brand_colors(kit.get("palette")),
            "voice": kit.get("voice") if isinstance(kit.get("voice"), str) else "",
        }
        self.conn.execute(
            "UPDATE projects SET brand_kit=? WHERE id=?",
            (json.dumps(cleaned, ensure_ascii=False), project_id),
        )
        self.conn.commit()
        return self.get_project(project_id)

    def create_thread(self, project_id: str, topic: str = "", mode: str = "fast") -> dict:
        tid = _id()
        self.conn.execute(
            "INSERT INTO threads (id, project_id, topic, mode, created_at) VALUES (?,?,?,?,?)",
            (tid, project_id, topic, mode, _now()),
        )
        self.conn.commit()
        return self.get_thread(tid)

    def list_threads(self, project_id: str) -> list[dict]:
        return self._rows(
            self.conn.execute(
                "SELECT * FROM threads WHERE project_id=? ORDER BY created_at DESC",
                (project_id,),
            ).fetchall()
        )

    def get_thread(self, thread_id: str) -> Optional[dict]:
        return self._row(self.conn.execute("SELECT * FROM threads WHERE id=?", (thread_id,)).fetchone())

    def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        plan: Any = None,
    ) -> dict:
        mid = _id()
        plan_json = json.dumps(plan, ensure_ascii=False) if plan is not None else None
        self.conn.execute(
            "INSERT INTO messages (id, thread_id, role, content, plan_json, created_at) VALUES (?,?,?,?,?,?)",
            (mid, thread_id, role, content, plan_json, _now()),
        )
        self.conn.commit()
        return self.get_message(mid)

    def get_message(self, message_id: str) -> dict:
        row = dict(self.conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone())
        if row.get("plan_json"):
            row["plan"] = json.loads(row["plan_json"])
        return row

    def list_messages(self, thread_id: str) -> list[dict]:
        rows = self._rows(
            self.conn.execute(
                "SELECT * FROM messages WHERE thread_id=? ORDER BY created_at ASC",
                (thread_id,),
            ).fetchall()
        )
        for row in rows:
            if row.get("plan_json"):
                row["plan"] = json.loads(row["plan_json"])
        return rows

    def add_artifact(self, **kwargs: Any) -> dict:
        aid = kwargs.get("id") or _id()
        self.conn.execute(
            """INSERT INTO artifacts
               (id, project_id, thread_id, kind, path, mime, prompt, provider, model, parent_id, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                aid,
                kwargs["project_id"],
                kwargs.get("thread_id"),
                kwargs.get("kind", "image"),
                kwargs.get("path", ""),
                kwargs.get("mime", "image/svg+xml"),
                kwargs.get("prompt", ""),
                kwargs.get("provider", ""),
                kwargs.get("model", ""),
                kwargs.get("parent_id"),
                _now(),
            ),
        )
        self.conn.commit()
        return dict(self.conn.execute("SELECT * FROM artifacts WHERE id=?", (aid,)).fetchone())

    def get_artifact(self, artifact_id: str) -> Optional[dict]:
        return self._row(
            self.conn.execute("SELECT * FROM artifacts WHERE id=?", (artifact_id,)).fetchone()
        )

    def add_node(self, **kwargs: Any) -> dict:
        from atelier.helix.loom import text_meta

        nid = kwargs.get("id") or _id()
        text = kwargs.get("text")
        if not text and kwargs.get("data") is not None:
            data = kwargs["data"]
            text = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        self.conn.execute(
            """INSERT INTO nodes (id, project_id, type, x, y, w, h, z, artifact_id, text, meta)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                nid,
                kwargs["project_id"],
                str(kwargs.get("type") or "image"),
                _finite(kwargs.get("x", 80), 80.0),
                _finite(kwargs.get("y", 80), 80.0),
                _finite(kwargs.get("w", 320), 320.0),
                _finite(kwargs.get("h", 240), 240.0),
                int(_finite(kwargs.get("z", 0), 0.0)),
                kwargs.get("artifact_id"),
                str(text) if text else "",
                json.dumps(text_meta(kwargs.get("meta")), ensure_ascii=False),
            ),
        )
        self.conn.commit()
        node = self.get_node(nid)
        self.push_undo(
            kwargs["project_id"],
            "add_node",
            {"node_id": nid, "artifact_id": kwargs.get("artifact_id")},
        )
        return node

    @staticmethod
    def _node_meta(raw: Any) -> dict:
        """Meta as a dict, whatever a row already on disk happens to hold.

        Rows written before meta was normalised can hold any string; a bare
        json.loads there raises inside list_nodes and 500s the whole board.
        """
        if isinstance(raw, dict):
            return raw
        try:
            parsed = json.loads(raw or "{}")
        except (TypeError, ValueError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def get_node(self, node_id: str) -> Optional[dict]:
        row = self._row(self.conn.execute("SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone())
        if not row:
            return None
        row["meta"] = self._node_meta(row.get("meta"))
        return row

    def list_nodes(self, project_id: str) -> list[dict]:
        rows = self._rows(
            self.conn.execute(
                "SELECT * FROM nodes WHERE project_id=? ORDER BY z ASC, id ASC",
                (project_id,),
            ).fetchall()
        )
        for row in rows:
            row["meta"] = self._node_meta(row.get("meta"))
        return rows

    def update_node(self, node_id: str, **fields: Any) -> Optional[dict]:
        from atelier.helix.loom import text_meta

        if "data" in fields and "text" not in fields:
            data = fields.pop("data")
            fields["text"] = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
        else:
            fields.pop("data", None)
        if not self.get_node(node_id):
            return None
        allowed = {"x", "y", "w", "h", "z", "text", "meta"}
        sets = []
        values = []
        for key, value in fields.items():
            if key not in allowed:
                continue
            if key == "meta":
                value = json.dumps(text_meta(self._node_meta(value)), ensure_ascii=False)
            elif key in {"x", "y", "w", "h", "z"}:
                number = _finite(value, None)
                if number is None:
                    continue  # a junk coordinate is a no-op, not a jump to the origin
                value = int(number) if key == "z" else number
            elif key == "text":
                if value is None:
                    continue
                value = str(value)
            sets.append(f"{key}=?")
            values.append(value)
        if sets:
            values.append(node_id)
            self.conn.execute(f"UPDATE nodes SET {', '.join(sets)} WHERE id=?", values)
            self.conn.commit()
        return self.get_node(node_id)

    def delete_node(self, node_id: str) -> bool:
        cur = self.conn.execute("DELETE FROM nodes WHERE id=?", (node_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def push_undo(self, project_id: str, action: str, payload: dict) -> dict:
        uid = _id()
        self.conn.execute(
            "INSERT INTO undo_log (id, project_id, action, payload, created_at) VALUES (?,?,?,?,?)",
            (uid, project_id, action, json.dumps(payload, ensure_ascii=False), _now()),
        )
        self.conn.commit()
        return {"id": uid, "action": action, "payload": payload}

    def undo(self, project_id: str) -> dict:
        row = self.conn.execute(
            "SELECT * FROM undo_log WHERE project_id=? ORDER BY created_at DESC, id DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if not row:
            return {"undone": False, "reason": "empty"}
        payload = json.loads(row["payload"] or "{}")
        if row["action"] == "add_node" and payload.get("node_id"):
            self.conn.execute("DELETE FROM nodes WHERE id=?", (payload["node_id"],))
        self.conn.execute("DELETE FROM undo_log WHERE id=?", (row["id"],))
        self.conn.commit()
        return {"undone": True, "action": row["action"], "payload": payload}

    def add_usage(self, **kwargs: Any) -> dict:
        uid = _id()
        self.conn.execute(
            """INSERT INTO usage_events
               (id, provider, model, unit_kind, units, estimated_usd, thread_id, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                uid,
                kwargs["provider"],
                kwargs.get("model", ""),
                kwargs.get("unit_kind", "tokens"),
                float(kwargs.get("units", 0)),
                float(kwargs.get("estimated_usd", 0)),
                kwargs.get("thread_id"),
                _now(),
            ),
        )
        self.conn.commit()
        return dict(self.conn.execute("SELECT * FROM usage_events WHERE id=?", (uid,)).fetchone())

    def list_usage(self, limit: int = 200) -> list[dict]:
        return self._rows(
            self.conn.execute(
                "SELECT * FROM usage_events ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        )

    def usage_totals(self) -> list[dict]:
        return self._rows(
            self.conn.execute(
                """SELECT provider, model, unit_kind,
                          SUM(units) AS units, SUM(estimated_usd) AS estimated_usd
                   FROM usage_events
                   GROUP BY provider, model, unit_kind"""
            ).fetchall()
        )
