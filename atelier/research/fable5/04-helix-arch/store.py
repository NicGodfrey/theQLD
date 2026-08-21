"""
store.py — Memory, the persistence module of Atelier's Helix architecture.

Pure Python standard library (sqlite3, json, hashlib, …). No dependencies.

Memory owns:
  * the SQLite database (schema in schema.sql, loaded verbatim from disk), and
  * the content-addressed blob root next to it (artifact bytes, deduplicated
    by sha256).

It is the only module allowed to touch either. Keyring, Spokes, Conductor,
Board and Loom all go through the methods below.

Invariants enforced here, in code (numbering matches ARCHITECTURE.md):
  I1  the store never learns a raw secret: provider configs are scanned and
      rejected if any field smells like an API key, token or private key.
  I7  a board may only project artifacts owned by its own project.
  I9  loom runs/steps only move along the legal status graph.
  I10 blob artifacts are content-addressed: bytes are stored once per sha256.

Usage:
    from store import MemoryStore
    with MemoryStore("/path/to/atelier.db") as mem:
        prj = mem.create_project("Nova rebrand")
        thr = mem.create_thread(prj["id"], title="Logo explorations")
        msg = mem.append_message(thr["id"], "user", "Try a bolder mark")

Run `python3 store.py` for a self-contained smoke demo against a temp db,
and `python3 test_store.py` for the invariant test suite.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import sqlite3
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class StoreError(Exception):
    """Base class for all Memory errors."""


class NotFound(StoreError):
    """The referenced row does not exist."""


class ValidationError(StoreError):
    """Input rejected before it reached SQLite."""


class SecretLeakError(ValidationError):
    """Something that looks like a raw secret was about to be persisted (I1)."""


class InvalidTransition(StoreError):
    """A loom run/step tried an illegal status change (I9)."""


# ---------------------------------------------------------------------------
# IDs and time
# ---------------------------------------------------------------------------

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def _ulid() -> str:
    """Lexicographically sortable 26-char ULID (48-bit ms time + 80-bit random)."""
    ts = int(time.time() * 1000) & ((1 << 48) - 1)
    n = (ts << 80) | int.from_bytes(os.urandom(10), "big")
    return "".join(_CROCKFORD[(n >> shift) & 31] for shift in range(125, -1, -5))


def _new_id(prefix: str) -> str:
    return f"{prefix}_{_ulid()}"


def _now_ms() -> int:
    return int(time.time() * 1000)


# ---------------------------------------------------------------------------
# Secret hygiene (I1)
# ---------------------------------------------------------------------------

_SECRET_VALUE_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),                # OpenAI-style
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{16,}"),            # Anthropic-style
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),                   # AWS access key id
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),           # GitHub tokens
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"),         # Slack tokens
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),               # Google API keys
    re.compile(r"\bhf_[A-Za-z0-9]{20,}"),                  # HuggingFace tokens
    re.compile(r"\br8_[A-Za-z0-9]{20,}"),                  # Replicate tokens
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),     # PEM material
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ"),           # JWTs
    re.compile(r"://[^/\s:@]+:[^/\s@]+@"),                 # userinfo in URLs
]

_SECRET_KEY_NAMES = {
    "api_key", "apikey", "api-key", "secret", "secret_key", "client_secret",
    "token", "access_token", "refresh_token", "password", "passwd",
    "authorization", "auth", "private_key", "credentials", "bearer",
}

_KEY_REF_RE = re.compile(r"^[a-z][a-z0-9_.:-]{2,63}$")


def _assert_no_secrets(value: Any, where: str) -> None:
    """Recursively refuse dicts/lists/strings that appear to carry raw secrets."""
    if isinstance(value, Mapping):
        for k, v in value.items():
            if isinstance(k, str) and k.strip().lower() in _SECRET_KEY_NAMES:
                raise SecretLeakError(
                    f"{where}: field {k!r} looks like a raw secret; store the "
                    f"secret in the Keyring and persist a key_ref instead (I1)"
                )
            _assert_no_secrets(v, f"{where}.{k}")
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _assert_no_secrets(v, f"{where}[{i}]")
    elif isinstance(value, str):
        for pat in _SECRET_VALUE_PATTERNS:
            if pat.search(value):
                raise SecretLeakError(
                    f"{where}: value matches secret pattern {pat.pattern!r}; "
                    f"raw secrets never enter Memory (I1)"
                )


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s[:60] or "project"


def _dump(value: Any, default: str) -> str:
    if value is None:
        return default
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _public(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """sqlite3.Row -> plain dict; '*_json' TEXT columns become parsed values."""
    if row is None:
        return None
    out: dict[str, Any] = {}
    for key in row.keys():
        val = row[key]
        if key.endswith("_json"):
            out[key[:-5]] = json.loads(val) if val is not None else None
        else:
            out[key] = val
    return out


_LOOM_FLOW = {
    "queued":    {"running", "cancelled", "skipped"},
    "running":   {"succeeded", "failed", "cancelled"},
    "succeeded": set(),
    "failed":    set(),
    "cancelled": set(),
    "skipped":   set(),
}


# ---------------------------------------------------------------------------
# The store
# ---------------------------------------------------------------------------


class MemoryStore:
    """Single-writer SQLite store + content-addressed blob root.

    Thread-safe for use from one process: all writes are serialized through
    an RLock and run in IMMEDIATE transactions.
    """

    def __init__(self, db_path: str | os.PathLike[str] = ":memory:",
                 blob_root: str | os.PathLike[str] | None = None) -> None:
        self._path = str(db_path)
        self._lock = threading.RLock()
        self._depth = 0

        self._db = sqlite3.connect(
            self._path, check_same_thread=False, isolation_level=None
        )
        self._db.row_factory = sqlite3.Row
        self._db.execute("PRAGMA foreign_keys = ON")
        self._db.execute("PRAGMA busy_timeout = 5000")
        if self._path != ":memory:":
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
        self._db.executescript(_SCHEMA_PATH.read_text(encoding="utf-8"))

        if blob_root is not None:
            self._blob_root = Path(blob_root)
        elif self._path == ":memory:":
            self._blob_root = Path(tempfile.mkdtemp(prefix="helix-blobs-"))
        else:
            self._blob_root = Path(self._path + ".blobs")
        self._blob_root.mkdir(parents=True, exist_ok=True)

    # -- lifecycle ----------------------------------------------------------

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> "MemoryStore":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- transactions -------------------------------------------------------

    @contextlib.contextmanager
    def _txn(self) -> Iterator[sqlite3.Connection]:
        """Re-entrant IMMEDIATE transaction; commit at the outermost exit."""
        with self._lock:
            if self._depth == 0:
                self._db.execute("BEGIN IMMEDIATE")
            self._depth += 1
            try:
                yield self._db
            except BaseException:
                self._depth -= 1
                if self._depth == 0:
                    self._db.execute("ROLLBACK")
                raise
            else:
                self._depth -= 1
                if self._depth == 0:
                    self._db.execute("COMMIT")

    def _one(self, sql: str, params: Sequence[Any] = ()) -> sqlite3.Row | None:
        return self._db.execute(sql, params).fetchone()

    def _require(self, table: str, row_id: str) -> sqlite3.Row:
        row = self._one(f"SELECT * FROM {table} WHERE id = ?", (row_id,))
        if row is None:
            raise NotFound(f"{table}: {row_id!r} not found")
        return row

    # ======================================================================
    # Projects
    # ======================================================================

    def create_project(self, name: str, description: str = "",
                       meta: Mapping[str, Any] | None = None) -> dict[str, Any]:
        now = _now_ms()
        base = _slugify(name)
        with self._txn():
            slug, n = base, 1
            while self._one("SELECT 1 FROM projects WHERE slug = ?", (slug,)):
                n += 1
                slug = f"{base}-{n}"
            pid = _new_id("prj")
            self._db.execute(
                "INSERT INTO projects (id, name, slug, description, meta_json,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
                (pid, name, slug, description, _dump(meta, "{}"), now, now),
            )
        return self.get_project(pid)

    def get_project(self, project_id: str) -> dict[str, Any]:
        return _public(self._require("projects", project_id))  # type: ignore[return-value]

    def get_project_by_slug(self, slug: str) -> dict[str, Any] | None:
        return _public(self._one("SELECT * FROM projects WHERE slug = ?", (slug,)))

    def list_projects(self, include_archived: bool = False) -> list[dict[str, Any]]:
        sql = "SELECT * FROM projects"
        if not include_archived:
            sql += " WHERE archived_at IS NULL"
        sql += " ORDER BY updated_at DESC"
        return [_public(r) for r in self._db.execute(sql)]  # type: ignore[misc]

    def update_project(self, project_id: str, *, name: str | None = None,
                       description: str | None = None,
                       meta: Mapping[str, Any] | None = None) -> dict[str, Any]:
        with self._txn():
            self._require("projects", project_id)
            sets, params = ["updated_at = ?"], [_now_ms()]
            if name is not None:
                sets.append("name = ?"); params.append(name)
            if description is not None:
                sets.append("description = ?"); params.append(description)
            if meta is not None:
                sets.append("meta_json = ?"); params.append(_dump(meta, "{}"))
            params.append(project_id)
            self._db.execute(
                f"UPDATE projects SET {', '.join(sets)} WHERE id = ?", params
            )
        return self.get_project(project_id)

    def archive_project(self, project_id: str) -> dict[str, Any]:
        with self._txn():
            self._require("projects", project_id)
            now = _now_ms()
            self._db.execute(
                "UPDATE projects SET archived_at = ?, updated_at = ? WHERE id = ?",
                (now, now, project_id),
            )
        return self.get_project(project_id)

    def unarchive_project(self, project_id: str) -> dict[str, Any]:
        with self._txn():
            self._require("projects", project_id)
            self._db.execute(
                "UPDATE projects SET archived_at = NULL, updated_at = ? WHERE id = ?",
                (_now_ms(), project_id),
            )
        return self.get_project(project_id)

    # ======================================================================
    # Threads (intent strand)
    # ======================================================================

    def create_thread(self, project_id: str,
                      title: str = "Untitled thread") -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            self._require("projects", project_id)
            tid = _new_id("thr")
            self._db.execute(
                "INSERT INTO threads (id, project_id, title, created_at,"
                " updated_at) VALUES (?,?,?,?,?)",
                (tid, project_id, title, now, now),
            )
        return self.get_thread(tid)

    def get_thread(self, thread_id: str) -> dict[str, Any]:
        return _public(self._require("threads", thread_id))  # type: ignore[return-value]

    def list_threads(self, project_id: str,
                     status: str | None = None) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM threads WHERE project_id = ?", [project_id]
        if status is not None:
            sql += " AND status = ?"; params.append(status)
        sql += " ORDER BY updated_at DESC"
        return [_public(r) for r in self._db.execute(sql, params)]  # type: ignore[misc]

    def set_thread_status(self, thread_id: str, status: str) -> dict[str, Any]:
        with self._txn():
            self._require("threads", thread_id)
            self._db.execute(
                "UPDATE threads SET status = ?, updated_at = ? WHERE id = ?",
                (status, _now_ms(), thread_id),
            )
        return self.get_thread(thread_id)

    def rename_thread(self, thread_id: str, title: str) -> dict[str, Any]:
        with self._txn():
            self._require("threads", thread_id)
            self._db.execute(
                "UPDATE threads SET title = ?, updated_at = ? WHERE id = ?",
                (title, _now_ms(), thread_id),
            )
        return self.get_thread(thread_id)

    # ======================================================================
    # Messages (intent strand, append-only)
    # ======================================================================

    def append_message(self, thread_id: str, role: str, content: str,
                       payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            self._require("threads", thread_id)
            seq = self._one(
                "SELECT COALESCE(MAX(seq), -1) + 1 AS s FROM messages"
                " WHERE thread_id = ?", (thread_id,)
            )["s"]
            mid = _new_id("msg")
            self._db.execute(
                "INSERT INTO messages (id, thread_id, seq, role, content,"
                " payload_json, created_at) VALUES (?,?,?,?,?,?,?)",
                (mid, thread_id, seq, role, content, _dump(payload, "{}"), now),
            )
            self._db.execute(
                "UPDATE threads SET updated_at = ? WHERE id = ?", (now, thread_id)
            )
        return _public(self._require("messages", mid))  # type: ignore[return-value]

    def list_messages(self, thread_id: str, after_seq: int = -1,
                      limit: int = 1000) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT * FROM messages WHERE thread_id = ? AND seq > ?"
            " ORDER BY seq LIMIT ?", (thread_id, after_seq, limit)
        )
        return [_public(r) for r in rows]  # type: ignore[misc]

    # -- rungs: message <-> artifact provenance -----------------------------

    def link_message_artifact(self, message_id: str, artifact_id: str,
                              relation: str = "produced") -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            self._require("messages", message_id)
            self._require("artifacts", artifact_id)
            rid = _new_id("rng")
            self._db.execute(
                "INSERT OR IGNORE INTO rungs (id, message_id, artifact_id,"
                " relation, created_at) VALUES (?,?,?,?,?)",
                (rid, message_id, artifact_id, relation, now),
            )
            row = self._one(
                "SELECT * FROM rungs WHERE message_id = ? AND artifact_id = ?"
                " AND relation = ?", (message_id, artifact_id, relation)
            )
        return _public(row)  # type: ignore[return-value]

    def artifact_rungs(self, artifact_id: str) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT r.*, m.thread_id, m.role, m.seq FROM rungs r"
            " JOIN messages m ON m.id = r.message_id"
            " WHERE r.artifact_id = ? ORDER BY r.created_at", (artifact_id,)
        )
        return [_public(r) for r in rows]  # type: ignore[misc]

    # ======================================================================
    # Artifacts (matter strand, content-addressed)
    # ======================================================================

    def _blob_write(self, data: bytes) -> tuple[str, str]:
        """Store bytes once per sha256 (I10). Returns (sha256, relative uri)."""
        sha = hashlib.sha256(data).hexdigest()
        rel = f"{sha[:2]}/{sha}"
        path = self._blob_root / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.parent / f".{sha}.tmp{os.urandom(4).hex()}"
            tmp.write_bytes(data)
            os.replace(tmp, path)
        return sha, rel

    def _validate_parent(self, project_id: str, parent_id: str | None) -> None:
        if parent_id is None:
            return
        parent = self._require("artifacts", parent_id)
        if parent["project_id"] != project_id:
            raise ValidationError(
                "artifact lineage cannot cross projects "
                f"({parent_id} belongs to {parent['project_id']})"
            )

    def put_artifact(self, project_id: str, data: bytes, kind: str, mime: str, *,
                     title: str = "", width: int | None = None,
                     height: int | None = None, duration_ms: int | None = None,
                     meta: Mapping[str, Any] | None = None,
                     parent_id: str | None = None) -> dict[str, Any]:
        """Write bytes into the blob root and register a new artifact row."""
        now = _now_ms()
        with self._txn():
            self._require("projects", project_id)
            self._validate_parent(project_id, parent_id)
            sha, rel = self._blob_write(data)
            aid = _new_id("art")
            self._db.execute(
                "INSERT INTO artifacts (id, project_id, kind, mime, storage,"
                " uri, sha256, byte_size, width, height, duration_ms, title,"
                " meta_json, parent_id, created_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (aid, project_id, kind, mime, "blob", rel, sha, len(data),
                 width, height, duration_ms, title, _dump(meta, "{}"),
                 parent_id, now),
            )
        return self.get_artifact(aid)

    def register_external_artifact(self, project_id: str, uri: str, kind: str,
                                   mime: str, *, title: str = "",
                                   sha256: str | None = None,
                                   byte_size: int | None = None,
                                   width: int | None = None,
                                   height: int | None = None,
                                   duration_ms: int | None = None,
                                   meta: Mapping[str, Any] | None = None,
                                   parent_id: str | None = None) -> dict[str, Any]:
        """Register an artifact whose bytes live elsewhere (a URL)."""
        _assert_no_secrets(uri, "artifact.uri")
        now = _now_ms()
        with self._txn():
            self._require("projects", project_id)
            self._validate_parent(project_id, parent_id)
            aid = _new_id("art")
            self._db.execute(
                "INSERT INTO artifacts (id, project_id, kind, mime, storage,"
                " uri, sha256, byte_size, width, height, duration_ms, title,"
                " meta_json, parent_id, created_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (aid, project_id, kind, mime, "external", uri, sha256,
                 byte_size, width, height, duration_ms, title,
                 _dump(meta, "{}"), parent_id, now),
            )
        return self.get_artifact(aid)

    def get_artifact(self, artifact_id: str) -> dict[str, Any]:
        return _public(self._require("artifacts", artifact_id))  # type: ignore[return-value]

    def open_artifact(self, artifact_id: str) -> bytes:
        row = self._require("artifacts", artifact_id)
        if row["storage"] != "blob":
            raise ValidationError(
                f"artifact {artifact_id} is external ({row['uri']}); fetch it yourself"
            )
        return (self._blob_root / row["uri"]).read_bytes()

    def annotate_artifact(self, artifact_id: str, *, title: str | None = None,
                          meta: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """The only legal artifact mutation: annotations (I4)."""
        with self._txn():
            self._require("artifacts", artifact_id)
            sets, params = [], []
            if title is not None:
                sets.append("title = ?"); params.append(title)
            if meta is not None:
                sets.append("meta_json = ?"); params.append(_dump(meta, "{}"))
            if sets:
                params.append(artifact_id)
                self._db.execute(
                    f"UPDATE artifacts SET {', '.join(sets)} WHERE id = ?", params
                )
        return self.get_artifact(artifact_id)

    def list_artifacts(self, project_id: str, kind: str | None = None,
                       limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM artifacts WHERE project_id = ?", [project_id]
        if kind is not None:
            sql += " AND kind = ?"; params.append(kind)
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        return [_public(r) for r in self._db.execute(sql, params)]  # type: ignore[misc]

    def artifact_lineage(self, artifact_id: str) -> dict[str, Any]:
        """Ancestors (derivation chain up) and descendants (variations down)."""
        self._require("artifacts", artifact_id)
        ancestors = self._db.execute(
            """
            WITH RECURSIVE up(id, depth) AS (
                SELECT parent_id, 1 FROM artifacts
                 WHERE id = ? AND parent_id IS NOT NULL
                UNION ALL
                SELECT a.parent_id, up.depth + 1
                  FROM artifacts a JOIN up ON a.id = up.id
                 WHERE a.parent_id IS NOT NULL
            )
            SELECT a.*, up.depth FROM up JOIN artifacts a ON a.id = up.id
            ORDER BY up.depth
            """,
            (artifact_id,),
        ).fetchall()
        descendants = self._db.execute(
            """
            WITH RECURSIVE down(id, depth) AS (
                SELECT id, 0 FROM artifacts WHERE id = ?
                UNION ALL
                SELECT a.id, down.depth + 1
                  FROM artifacts a JOIN down ON a.parent_id = down.id
            )
            SELECT a.*, down.depth FROM down JOIN artifacts a ON a.id = down.id
            WHERE down.depth > 0 ORDER BY down.depth, a.created_at
            """,
            (artifact_id,),
        ).fetchall()
        return {
            "artifact_id": artifact_id,
            "ancestors": [_public(r) for r in ancestors],
            "descendants": [_public(r) for r in descendants],
        }

    # ======================================================================
    # Board (infinite canvas: mutable projection of the helix)
    # ======================================================================

    def create_board(self, project_id: str, name: str = "Board",
                     viewport: Mapping[str, Any] | None = None) -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            self._require("projects", project_id)
            bid = _new_id("brd")
            self._db.execute(
                "INSERT INTO boards (id, project_id, name, viewport_json,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (bid, project_id, name,
                 _dump(viewport, '{"x":0,"y":0,"zoom":1}'), now, now),
            )
        return self.get_board(bid)

    def get_board(self, board_id: str) -> dict[str, Any]:
        return _public(self._require("boards", board_id))  # type: ignore[return-value]

    def list_boards(self, project_id: str) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT * FROM boards WHERE project_id = ? ORDER BY created_at",
            (project_id,),
        )
        return [_public(r) for r in rows]  # type: ignore[misc]

    def set_viewport(self, board_id: str,
                     viewport: Mapping[str, Any]) -> dict[str, Any]:
        with self._txn():
            self._require("boards", board_id)
            self._db.execute(
                "UPDATE boards SET viewport_json = ?, updated_at = ? WHERE id = ?",
                (_dump(viewport, "{}"), _now_ms(), board_id),
            )
        return self.get_board(board_id)

    def create_layer(self, board_id: str, name: str = "Layer",
                     z_index: int | None = None) -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            self._require("boards", board_id)
            if z_index is None:
                z_index = self._one(
                    "SELECT COALESCE(MAX(z_index), -1) + 1 AS z"
                    " FROM board_layers WHERE board_id = ?", (board_id,)
                )["z"]
            lid = _new_id("lyr")
            self._db.execute(
                "INSERT INTO board_layers (id, board_id, name, z_index,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (lid, board_id, name, z_index, now, now),
            )
        return _public(self._require("board_layers", lid))  # type: ignore[return-value]

    def update_layer(self, layer_id: str, *, name: str | None = None,
                     z_index: int | None = None, visible: bool | None = None,
                     locked: bool | None = None) -> dict[str, Any]:
        with self._txn():
            self._require("board_layers", layer_id)
            sets, params = ["updated_at = ?"], [_now_ms()]
            if name is not None:
                sets.append("name = ?"); params.append(name)
            if z_index is not None:
                sets.append("z_index = ?"); params.append(z_index)
            if visible is not None:
                sets.append("visible = ?"); params.append(int(visible))
            if locked is not None:
                sets.append("locked = ?"); params.append(int(locked))
            params.append(layer_id)
            self._db.execute(
                f"UPDATE board_layers SET {', '.join(sets)} WHERE id = ?", params
            )
        return _public(self._require("board_layers", layer_id))  # type: ignore[return-value]

    def delete_layer(self, layer_id: str) -> None:
        with self._txn():
            self._require("board_layers", layer_id)
            self._db.execute("DELETE FROM board_layers WHERE id = ?", (layer_id,))

    def add_node(self, board_id: str, layer_id: str, kind: str, *,
                 artifact_id: str | None = None, x: float = 0, y: float = 0,
                 w: float = 100, h: float = 100, rotation: float = 0,
                 opacity: float = 1.0, z: float | None = None,
                 props: Mapping[str, Any] | None = None) -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            board = self._require("boards", board_id)
            layer = self._require("board_layers", layer_id)
            if layer["board_id"] != board_id:
                raise ValidationError(
                    f"layer {layer_id} belongs to board {layer['board_id']}, "
                    f"not {board_id}"
                )
            if artifact_id is not None:
                art = self._require("artifacts", artifact_id)
                if art["project_id"] != board["project_id"]:
                    raise ValidationError(
                        "a board may only project artifacts from its own "
                        f"project (I7): {artifact_id} belongs to "
                        f"{art['project_id']}"
                    )
            if z is None:
                z = self._one(
                    "SELECT COALESCE(MAX(z), 0) + 1 AS z FROM board_nodes"
                    " WHERE layer_id = ?", (layer_id,)
                )["z"]
            nid = _new_id("nod")
            self._db.execute(
                "INSERT INTO board_nodes (id, board_id, layer_id, kind,"
                " artifact_id, x, y, w, h, rotation, opacity, z, props_json,"
                " created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (nid, board_id, layer_id, kind, artifact_id, x, y, w, h,
                 rotation, opacity, z, _dump(props, "{}"), now, now),
            )
        return self.get_node(nid)

    def get_node(self, node_id: str) -> dict[str, Any]:
        return _public(self._require("board_nodes", node_id))  # type: ignore[return-value]

    _NODE_FIELDS = {"x", "y", "w", "h", "rotation", "opacity", "z", "layer_id"}

    def update_node(self, node_id: str, *, props: Mapping[str, Any] | None = None,
                    **fields: Any) -> dict[str, Any]:
        unknown = set(fields) - self._NODE_FIELDS
        if unknown:
            raise ValidationError(f"unknown node fields: {sorted(unknown)}")
        with self._txn():
            node = self._require("board_nodes", node_id)
            if "layer_id" in fields:
                layer = self._require("board_layers", fields["layer_id"])
                if layer["board_id"] != node["board_id"]:
                    raise ValidationError("cannot move a node across boards")
            sets, params = ["updated_at = ?"], [_now_ms()]
            for key, val in fields.items():
                sets.append(f"{key} = ?"); params.append(val)
            if props is not None:
                sets.append("props_json = ?"); params.append(_dump(props, "{}"))
            params.append(node_id)
            self._db.execute(
                f"UPDATE board_nodes SET {', '.join(sets)} WHERE id = ?", params
            )
        return self.get_node(node_id)

    def delete_node(self, node_id: str) -> None:
        with self._txn():
            self._require("board_nodes", node_id)
            self._db.execute("DELETE FROM board_nodes WHERE id = ?", (node_id,))

    def board_scene(self, board_id: str) -> list[dict[str, Any]]:
        """Everything a renderer needs, in paint order (layer z, then node z)."""
        self._require("boards", board_id)
        rows = self._db.execute(
            "SELECT * FROM v_board_scene WHERE board_id = ?"
            " ORDER BY layer_z, node_z", (board_id,)
        )
        return [_public(r) for r in rows]  # type: ignore[misc]

    # ======================================================================
    # Brand kits
    # ======================================================================

    def create_brand_kit(self, project_id: str, name: str, *,
                         palette: Sequence[Any] | None = None,
                         typography: Mapping[str, Any] | None = None,
                         voice: Mapping[str, Any] | None = None,
                         activate: bool = False) -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            self._require("projects", project_id)
            kid = _new_id("bkt")
            self._db.execute(
                "INSERT INTO brand_kits (id, project_id, name, palette_json,"
                " typography_json, voice_json, created_at, updated_at)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (kid, project_id, name, _dump(palette, "[]"),
                 _dump(typography, "{}"), _dump(voice, "{}"), now, now),
            )
            if activate:
                self._activate_brand_kit_locked(kid, project_id)
        return self.get_brand_kit(kid)

    def _activate_brand_kit_locked(self, brand_kit_id: str, project_id: str) -> None:
        now = _now_ms()
        self._db.execute(
            "UPDATE brand_kits SET is_active = 0, updated_at = ?"
            " WHERE project_id = ? AND is_active = 1", (now, project_id)
        )
        self._db.execute(
            "UPDATE brand_kits SET is_active = 1, updated_at = ? WHERE id = ?",
            (now, brand_kit_id),
        )

    def activate_brand_kit(self, brand_kit_id: str) -> dict[str, Any]:
        with self._txn():
            kit = self._require("brand_kits", brand_kit_id)
            self._activate_brand_kit_locked(brand_kit_id, kit["project_id"])
        return self.get_brand_kit(brand_kit_id)

    def get_active_brand_kit(self, project_id: str) -> dict[str, Any] | None:
        row = self._one(
            "SELECT * FROM brand_kits WHERE project_id = ? AND is_active = 1",
            (project_id,),
        )
        return self.get_brand_kit(row["id"]) if row else None

    def get_brand_kit(self, brand_kit_id: str) -> dict[str, Any]:
        kit = _public(self._require("brand_kits", brand_kit_id))
        assert kit is not None
        rows = self._db.execute(
            "SELECT ba.id, ba.role, ba.artifact_id, ba.created_at,"
            " a.kind, a.mime, a.uri, a.title FROM brand_assets ba"
            " JOIN artifacts a ON a.id = ba.artifact_id"
            " WHERE ba.brand_kit_id = ? ORDER BY ba.created_at",
            (brand_kit_id,),
        )
        kit["assets"] = [_public(r) for r in rows]
        return kit

    def list_brand_kits(self, project_id: str) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT id FROM brand_kits WHERE project_id = ?"
            " ORDER BY created_at", (project_id,)
        ).fetchall()
        return [self.get_brand_kit(r["id"]) for r in rows]

    def add_brand_asset(self, brand_kit_id: str, artifact_id: str,
                        role: str = "reference") -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            kit = self._require("brand_kits", brand_kit_id)
            art = self._require("artifacts", artifact_id)
            if art["project_id"] != kit["project_id"]:
                raise ValidationError(
                    "brand assets must come from the brand kit's own project"
                )
            self._db.execute(
                "INSERT OR IGNORE INTO brand_assets (id, brand_kit_id,"
                " artifact_id, role, created_at) VALUES (?,?,?,?,?)",
                (_new_id("bas"), brand_kit_id, artifact_id, role, now),
            )
        return self.get_brand_kit(brand_kit_id)

    def remove_brand_asset(self, brand_asset_id: str) -> None:
        with self._txn():
            self._require("brand_assets", brand_asset_id)
            self._db.execute(
                "DELETE FROM brand_assets WHERE id = ?", (brand_asset_id,)
            )

    # ======================================================================
    # Provider configs (Spokes registry; BYOK — key_ref only, never secrets)
    # ======================================================================

    def upsert_provider_config(self, spoke: str, label: str, *,
                               key_ref: str | None = None,
                               base_url: str | None = None,
                               capabilities: Sequence[str] | None = None,
                               defaults: Mapping[str, Any] | None = None,
                               enabled: bool = True) -> dict[str, Any]:
        if key_ref is not None and not _KEY_REF_RE.match(key_ref):
            raise ValidationError(
                f"key_ref {key_ref!r} must match {_KEY_REF_RE.pattern} — it is "
                "a Keyring handle, not the secret itself"
            )
        _assert_no_secrets(
            {"key_ref": "", "base_url": base_url or "",
             "capabilities": list(capabilities or []),
             "defaults": dict(defaults or {}), "label": label},
            "provider_config",
        )
        # key_ref is scanned separately (its *value* must not be a raw key).
        if key_ref is not None:
            _assert_no_secrets(key_ref, "provider_config.key_ref")

        now = _now_ms()
        with self._txn():
            existing = self._one(
                "SELECT id FROM provider_configs WHERE label = ?", (label,)
            )
            if existing:
                pcid = existing["id"]
                self._db.execute(
                    "UPDATE provider_configs SET spoke = ?, base_url = ?,"
                    " key_ref = ?, enabled = ?, capabilities_json = ?,"
                    " defaults_json = ?, updated_at = ? WHERE id = ?",
                    (spoke, base_url, key_ref, int(enabled),
                     _dump(list(capabilities or []), "[]"),
                     _dump(defaults, "{}"), now, pcid),
                )
            else:
                pcid = _new_id("pcf")
                self._db.execute(
                    "INSERT INTO provider_configs (id, spoke, label, base_url,"
                    " key_ref, enabled, capabilities_json, defaults_json,"
                    " created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (pcid, spoke, label, base_url, key_ref, int(enabled),
                     _dump(list(capabilities or []), "[]"),
                     _dump(defaults, "{}"), now, now),
                )
        return self.get_provider_config(pcid)

    def get_provider_config(self, provider_config_id: str) -> dict[str, Any]:
        return _public(self._require("provider_configs", provider_config_id))  # type: ignore[return-value]

    def list_provider_configs(self, spoke: str | None = None,
                              enabled_only: bool = False) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM provider_configs WHERE 1=1", []
        if spoke is not None:
            sql += " AND spoke = ?"; params.append(spoke)
        if enabled_only:
            sql += " AND enabled = 1"
        sql += " ORDER BY spoke, label"
        return [_public(r) for r in self._db.execute(sql, params)]  # type: ignore[misc]

    def set_provider_enabled(self, provider_config_id: str,
                             enabled: bool) -> dict[str, Any]:
        with self._txn():
            self._require("provider_configs", provider_config_id)
            self._db.execute(
                "UPDATE provider_configs SET enabled = ?, updated_at = ?"
                " WHERE id = ?", (int(enabled), _now_ms(), provider_config_id)
            )
        return self.get_provider_config(provider_config_id)

    # ======================================================================
    # Usage events (append-only metering ledger)
    # ======================================================================

    def record_usage(self, spoke: str, operation: str, *,
                     project_id: str | None = None, thread_id: str | None = None,
                     run_id: str | None = None, step_id: str | None = None,
                     provider_config_id: str | None = None,
                     model: str | None = None, unit_type: str = "requests",
                     input_units: int = 0, output_units: int = 0,
                     cost_micros: int = 0, latency_ms: int | None = None,
                     status: str = "ok", error: str | None = None,
                     meta: Mapping[str, Any] | None = None) -> dict[str, Any]:
        now = _now_ms()
        with self._txn():
            uid = _new_id("use")
            self._db.execute(
                "INSERT INTO usage_events (id, created_at, project_id,"
                " thread_id, run_id, step_id, provider_config_id, spoke,"
                " operation, model, unit_type, input_units, output_units,"
                " cost_micros, latency_ms, status, error, meta_json)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (uid, now, project_id, thread_id, run_id, step_id,
                 provider_config_id, spoke, operation, model, unit_type,
                 input_units, output_units, cost_micros, latency_ms, status,
                 error, _dump(meta, "{}")),
            )
        return _public(self._require("usage_events", uid))  # type: ignore[return-value]

    def list_usage_events(self, project_id: str | None = None,
                          since_ms: int | None = None,
                          limit: int = 500) -> list[dict[str, Any]]:
        sql, params = "SELECT * FROM usage_events WHERE 1=1", []
        if project_id is not None:
            sql += " AND project_id = ?"; params.append(project_id)
        if since_ms is not None:
            sql += " AND created_at >= ?"; params.append(since_ms)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        return [_public(r) for r in self._db.execute(sql, params)]  # type: ignore[misc]

    def usage_summary(self, project_id: str | None = None,
                      since_ms: int | None = None) -> list[dict[str, Any]]:
        sql, params = (
            "SELECT spoke, operation, COUNT(*) AS events,"
            " SUM(input_units) AS input_units, SUM(output_units) AS output_units,"
            " SUM(cost_micros) AS cost_micros, AVG(latency_ms) AS avg_latency_ms"
            " FROM usage_events WHERE 1=1", []
        )
        if project_id is not None:
            sql += " AND project_id = ?"; params.append(project_id)
        if since_ms is not None:
            sql += " AND created_at >= ?"; params.append(since_ms)
        sql += " GROUP BY spoke, operation ORDER BY cost_micros DESC"
        return [dict(r) for r in self._db.execute(sql, params)]

    def usage_daily(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self._db.execute(
            "SELECT * FROM v_usage_daily ORDER BY day, spoke, operation"
        )]

    # ======================================================================
    # Loom (pipeline runs)
    # ======================================================================

    def create_run(self, project_id: str,
                   steps: Sequence[Mapping[str, Any]], *,
                   thread_id: str | None = None, name: str = "run",
                   plan: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """steps: [{'name', 'spoke_op', 'provider_config_id'?, 'params'?}, …]"""
        if not steps:
            raise ValidationError("a loom run needs at least one step")
        now = _now_ms()
        with self._txn():
            self._require("projects", project_id)
            if thread_id is not None:
                self._require("threads", thread_id)
            rid = _new_id("run")
            self._db.execute(
                "INSERT INTO loom_runs (id, project_id, thread_id, name,"
                " plan_json, created_at) VALUES (?,?,?,?,?,?)",
                (rid, project_id, thread_id, name, _dump(plan, "{}"), now),
            )
            for idx, step in enumerate(steps):
                self._db.execute(
                    "INSERT INTO loom_steps (id, run_id, idx, name, spoke_op,"
                    " provider_config_id, params_json) VALUES (?,?,?,?,?,?,?)",
                    (_new_id("stp"), rid, idx,
                     step.get("name", f"step-{idx}"), step["spoke_op"],
                     step.get("provider_config_id"),
                     _dump(step.get("params"), "{}")),
                )
        return self.get_run(rid)

    def _transition(self, table: str, row_id: str, new_status: str,
                    extra_sets: str = "", extra_params: Sequence[Any] = ()) -> None:
        row = self._require(table, row_id)
        allowed = _LOOM_FLOW.get(row["status"], set())
        if new_status not in allowed:
            raise InvalidTransition(
                f"{table} {row_id}: {row['status']!r} -> {new_status!r} is not "
                f"a legal move (allowed: {sorted(allowed)}) (I9)"
            )
        self._db.execute(
            f"UPDATE {table} SET status = ?{extra_sets} WHERE id = ?",
            [new_status, *extra_params, row_id],
        )

    def start_run(self, run_id: str) -> dict[str, Any]:
        with self._txn():
            self._transition("loom_runs", run_id, "running",
                             ", started_at = ?", (_now_ms(),))
        return self.get_run(run_id)

    def finish_run(self, run_id: str, status: str = "succeeded",
                   error: str | None = None) -> dict[str, Any]:
        with self._txn():
            self._transition("loom_runs", run_id, status,
                             ", finished_at = ?, error = ?", (_now_ms(), error))
        return self.get_run(run_id)

    def start_step(self, step_id: str) -> dict[str, Any]:
        with self._txn():
            self._transition("loom_steps", step_id, "running",
                             ", started_at = ?", (_now_ms(),))
        return _public(self._require("loom_steps", step_id))  # type: ignore[return-value]

    def add_step_inputs(self, step_id: str,
                        artifact_ids: Sequence[str]) -> None:
        with self._txn():
            self._require("loom_steps", step_id)
            for aid in artifact_ids:
                self._require("artifacts", aid)
                self._db.execute(
                    "INSERT OR IGNORE INTO loom_step_io (step_id, artifact_id,"
                    " direction) VALUES (?,?,'input')", (step_id, aid)
                )

    def finish_step(self, step_id: str, status: str = "succeeded", *,
                    output_artifact_ids: Sequence[str] = (),
                    error: str | None = None) -> dict[str, Any]:
        with self._txn():
            self._transition("loom_steps", step_id, status,
                             ", finished_at = ?, error = ?", (_now_ms(), error))
            for aid in output_artifact_ids:
                self._require("artifacts", aid)
                self._db.execute(
                    "INSERT OR IGNORE INTO loom_step_io (step_id, artifact_id,"
                    " direction) VALUES (?,?,'output')", (step_id, aid)
                )
        return _public(self._require("loom_steps", step_id))  # type: ignore[return-value]

    def get_run(self, run_id: str) -> dict[str, Any]:
        run = _public(self._require("loom_runs", run_id))
        assert run is not None
        steps = []
        for srow in self._db.execute(
            "SELECT * FROM loom_steps WHERE run_id = ? ORDER BY idx", (run_id,)
        ):
            step = _public(srow)
            assert step is not None
            io = self._db.execute(
                "SELECT artifact_id, direction FROM loom_step_io"
                " WHERE step_id = ?", (step["id"],)
            ).fetchall()
            step["inputs"] = [r["artifact_id"] for r in io
                              if r["direction"] == "input"]
            step["outputs"] = [r["artifact_id"] for r in io
                               if r["direction"] == "output"]
            steps.append(step)
        run["steps"] = steps
        return run

    def list_runs(self, project_id: str, limit: int = 50) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT id FROM loom_runs WHERE project_id = ?"
            " ORDER BY created_at DESC LIMIT ?", (project_id, limit)
        ).fetchall()
        return [self.get_run(r["id"]) for r in rows]

    # ======================================================================
    # Snapshot (whole-project export; used by GET /projects/{id}/snapshot)
    # ======================================================================

    def project_snapshot(self, project_id: str) -> dict[str, Any]:
        project = self.get_project(project_id)
        threads = []
        for thr in self.list_threads(project_id):
            thr = dict(thr)
            thr["messages"] = self.list_messages(thr["id"])
            threads.append(thr)
        boards = []
        for brd in self.list_boards(project_id):
            brd = dict(brd)
            brd["layers"] = [_public(r) for r in self._db.execute(
                "SELECT * FROM board_layers WHERE board_id = ?"
                " ORDER BY z_index", (brd["id"],)
            )]
            brd["nodes"] = self.board_scene(brd["id"])
            boards.append(brd)
        return {
            "format": "helix-snapshot/1",
            "exported_at": _now_ms(),
            "project": project,
            "threads": threads,
            "artifacts": self.list_artifacts(project_id, limit=100000),
            "boards": boards,
            "brand_kits": self.list_brand_kits(project_id),
            "runs": self.list_runs(project_id, limit=100000),
            "usage_summary": self.usage_summary(project_id=project_id),
        }


# ---------------------------------------------------------------------------
# Smoke demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import pprint

    with tempfile.TemporaryDirectory(prefix="helix-demo-") as tmp:
        with MemoryStore(os.path.join(tmp, "atelier.db")) as mem:
            prj = mem.create_project("Nova Coffee rebrand",
                                     description="Full identity refresh")
            thr = mem.create_thread(prj["id"], title="Logo explorations")
            ask = mem.append_message(thr["id"], "user",
                                     "Explore a bolder mark, keep the ember orange.")

            pc = mem.upsert_provider_config(
                "openai", "OpenAI (personal)", key_ref="openai.personal",
                capabilities=["text.generate", "image.generate"],
                defaults={"image_model": "gpt-image-1"},
            )

            run = mem.create_run(
                prj["id"],
                [{"name": "generate", "spoke_op": "image.generate",
                  "provider_config_id": pc["id"],
                  "params": {"prompt": "bold ember-orange coffee logo"}}],
                thread_id=thr["id"], name="logo-v2",
            )
            mem.start_run(run["id"])
            step = run["steps"][0]
            mem.start_step(step["id"])

            art = mem.put_artifact(prj["id"], b"\x89PNG-fake-bytes", "image",
                                   "image/png", title="Logo v2 candidate",
                                   width=1024, height=1024)
            mem.finish_step(step["id"], output_artifact_ids=[art["id"]])
            mem.finish_run(run["id"])
            reply = mem.append_message(thr["id"], "conductor",
                                       "Here is a bolder candidate.",
                                       payload={"artifact_ids": [art["id"]]})
            mem.link_message_artifact(reply["id"], art["id"], "produced")
            mem.record_usage("openai", "image.generate", project_id=prj["id"],
                             thread_id=thr["id"], run_id=run["id"],
                             step_id=step["id"], provider_config_id=pc["id"],
                             model="gpt-image-1", unit_type="pixels",
                             output_units=1024 * 1024, cost_micros=40000,
                             latency_ms=9000)

            brd = mem.create_board(prj["id"], "Moodboard")
            lyr = mem.create_layer(brd["id"], "Candidates")
            mem.add_node(brd["id"], lyr["id"], "artifact",
                         artifact_id=art["id"], x=120, y=80, w=512, h=512)

            kit = mem.create_brand_kit(
                prj["id"], "Nova core",
                palette=[{"name": "ember", "hex": "#E8590C"}],
                typography={"display": "Archivo Black"},
                voice={"adjectives": ["bold", "warm"]}, activate=True,
            )
            mem.add_brand_asset(kit["id"], art["id"], "logo_primary")

            snap = mem.project_snapshot(prj["id"])
            print("--- helix smoke demo: project snapshot summary ---")
            pprint.pprint({
                "project": snap["project"]["name"],
                "threads": len(snap["threads"]),
                "messages": sum(len(t["messages"]) for t in snap["threads"]),
                "artifacts": len(snap["artifacts"]),
                "boards": len(snap["boards"]),
                "nodes": sum(len(b["nodes"]) for b in snap["boards"]),
                "brand_kits": len(snap["brand_kits"]),
                "runs": len(snap["runs"]),
                "usage": snap["usage_summary"],
            })
