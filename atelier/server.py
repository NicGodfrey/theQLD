#!/usr/bin/env python3
"""Atelier local studio — Helix HTTP surface. Official BYOK hosts only."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
REPO = ROOT.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from atelier.helix.catalog import public as catalog_public
from atelier.helix.conductor import Conductor
from atelier.helix.keyring import Keyring
from atelier.helix.store import Memory


def runtime_dir() -> Path:
    raw = os.environ.get("ATELIER_RUNTIME")
    path = Path(raw) if raw else ROOT / ".runtime"
    path.mkdir(parents=True, exist_ok=True)
    (path / "artifacts").mkdir(exist_ok=True)
    return path


class App:
    def __init__(self):
        rt = runtime_dir()
        self.memory = Memory(rt / "helix.sqlite")
        self.keyring = Keyring()
        self.artifacts = rt / "artifacts"
        self.conductor = Conductor(self.memory, self.keyring, self.artifacts)
        if not self.memory.list_projects():
            project = self.memory.create_project(
                "Atelier Studio",
                brand_kit={
                    "name": "Atelier",
                    "palette": ["#0c0d10", "#f4f1ea", "#d4a373", "#7c9a92"],
                    "voice": "quiet, precise, editorial",
                },
            )
            self.memory.create_thread(project["id"], topic="First cloth", mode="fast")


APP = App()


def _json(handler: BaseHTTPRequestHandler, code: int, payload: Any) -> None:
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if not length:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _send_file(handler: BaseHTTPRequestHandler, path: Path, download_name: str | None = None) -> None:
    if not path.exists() or not path.is_file():
        _json(handler, 404, {"error": "not found"})
        return
    data = path.read_bytes()
    mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    if path.suffix == ".svg":
        mime = "image/svg+xml"
    handler.send_response(200)
    handler.send_header("Content-Type", mime)
    handler.send_header("Content-Length", str(len(data)))
    if download_name:
        handler.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("atelier %s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/index.html"}:
            _send_file(self, WEB / "index.html")
            return
        if path.startswith("/web/"):
            _send_file(self, WEB / path[len("/web/") :])
            return
        if path.startswith("/assets/"):
            _send_file(self, WEB / path[len("/assets/") :])
            return
        if path in {"/app.js", "/styles.css"}:
            _send_file(self, WEB / path.lstrip("/"))
            return
        if path == "/api/health":
            _json(self, 200, {"ok": True, "name": "atelier", "architecture": "helix"})
            return
        if path == "/api/keys":
            _json(self, 200, APP.keyring.public_status())
            return
        if path == "/api/projects":
            _json(self, 200, {"projects": APP.memory.list_projects()})
            return
        if path == "/api/catalog":
            _json(self, 200, catalog_public())
            return
        if path == "/api/usage":
            _json(self, 200, {"events": APP.memory.list_usage(), "totals": APP.memory.usage_totals()})
            return
        parts = [p for p in path.split("/") if p]
        if parts[:2] == ["api", "projects"] and len(parts) == 3:
            project = APP.memory.get_project(parts[2])
            _json(self, 200 if project else 404, project or {"error": "missing project"})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "threads":
            _json(self, 200, {"threads": APP.memory.list_threads(parts[2])})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "board":
            nodes = APP.memory.list_nodes(parts[2])
            _json(self, 200, {"nodes": nodes})
            return
        if parts[:2] == ["api", "threads"] and len(parts) == 4 and parts[3] == "messages":
            _json(self, 200, {"messages": APP.memory.list_messages(parts[2])})
            return
        if parts[:2] == ["api", "artifacts"] and len(parts) == 3:
            art = APP.memory.get_artifact(parts[2])
            if not art:
                _json(self, 404, {"error": "missing artifact"})
                return
            _send_file(self, Path(art["path"]), download_name=f"{art['id']}.bin")
            return
        if path.startswith("/api/"):
            _json(self, 404, {"error": "unknown GET"})
            return
        candidate = WEB / path.lstrip("/")
        if candidate.exists():
            _send_file(self, candidate)
            return
        _json(self, 404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = _read_json(self)
        except json.JSONDecodeError:
            _json(self, 400, {"error": "invalid json"})
            return
        parts = [p for p in path.split("/") if p]

        if path == "/api/keys":
            _json(
                self,
                200,
                APP.keyring.put(
                    body.get("provider", ""),
                    key=body.get("key") or "",
                    base_url=body.get("base_url") or "",
                ),
            )
            return
        if path == "/api/projects":
            project = APP.memory.create_project(body.get("name") or "Untitled")
            APP.memory.create_thread(project["id"], topic="New thread", mode=body.get("mode") or "fast")
            _json(self, 201, project)
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "threads":
            thread = APP.memory.create_thread(
                parts[2],
                topic=body.get("topic") or "",
                mode=body.get("mode") or "fast",
            )
            _json(self, 201, thread)
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "brand":
            _json(self, 200, APP.memory.update_brand_kit(parts[2], body.get("brand_kit") or body))
            return
        if parts[:2] == ["api", "threads"] and len(parts) == 4 and parts[3] == "run":
            thread = APP.memory.get_thread(parts[2])
            if not thread:
                _json(self, 404, {"error": "missing thread"})
                return
            try:
                result = APP.conductor.run(
                    project_id=thread["project_id"],
                    thread_id=thread["id"],
                    prompt=body.get("prompt") or "",
                    mode=body.get("mode") or thread.get("mode") or "fast",
                    provider=body.get("provider") or "demo",
                    model=body.get("model") or "",
                )
            except Exception as exc:
                _json(self, 500, {"error": str(exc)})
                return
            _json(self, 200, result)
            return
        if parts[:2] == ["api", "nodes"] and len(parts) == 3:
            node = APP.memory.update_node(parts[2], **{k: body[k] for k in body})
            _json(self, 200, node)
            return
        _json(self, 404, {"error": "unknown POST"})

    def do_PATCH(self) -> None:
        self.do_POST()


def main() -> None:
    host = os.environ.get("ATELIER_HOST", "127.0.0.1")
    port = int(os.environ.get("ATELIER_PORT", "8765"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Atelier Helix on http://{host}:{port}", flush=True)
    print("BYOK: OPENAI_API_KEY / GEMINI_API_KEY or Settings panel", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstop", flush=True)


if __name__ == "__main__":
    main()
