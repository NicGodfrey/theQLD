#!/usr/bin/env python3
"""Atelier local studio — Helix HTTP surface. Official BYOK hosts only."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import sys
import threading
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
from atelier.helix.conductor import Conductor, ConductorError
from atelier.helix.exportfmt import FormatError, export_artifact_bytes, export_project_bytes, export_scale
from atelier.helix.keyring import Keyring
from atelier.helix.loom import download_filename, ext_for_mime, write_bytes
from atelier.helix.paths import safe_under
from atelier.helix.quote import as_int, quote_run
from atelier.helix.store import Memory
from atelier.helix.usage import BudgetExceeded


LOCAL_BINDS = frozenset({"127.0.0.1", "localhost", "::1"})


def runtime_dir() -> Path:
    raw = os.environ.get("ATELIER_RUNTIME")
    path = Path(raw) if raw else ROOT / ".runtime"
    path.mkdir(parents=True, exist_ok=True)
    (path / "artifacts").mkdir(exist_ok=True)
    return path


class App:
    def __init__(self):
        rt = runtime_dir()
        self.lock = threading.RLock()
        self.memory = Memory(rt / "helix.sqlite")
        self.keyring = Keyring()
        self.artifacts = rt / "artifacts"
        self.artifacts.mkdir(parents=True, exist_ok=True)
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


APP: App | None = None


def get_app() -> App:
    global APP
    if APP is None:
        APP = App()
    return APP


def reset_app() -> App:
    global APP
    if APP is not None:
        try:
            APP.memory.close()
        except Exception:
            pass
    APP = App()
    return APP


APP = App()


def _json(handler: BaseHTTPRequestHandler, code: int, payload: Any) -> None:
    body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


# Upload bodies are base64 JSON; 5 MB of raw bytes is ~6.7 MB encoded.
# Anything past this is rejected before json/base64 work touches it.
MAX_JSON_BODY = 8_000_000

# Mimes we serve back verbatim from /api/artifacts. Anything else (notably
# text/html) is stored as octet-stream so an upload can never execute
# on the app origin. SVG stays allowed: _send_file sandboxes it via CSP.
UPLOAD_MIME_OK = {"application/pdf", "text/plain", "application/json"}


class BodyTooLarge(ValueError):
    pass


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if not length:
        return {}
    if length > MAX_JSON_BODY:
        remaining = length
        while remaining > 0:
            chunk = handler.rfile.read(min(65536, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
        raise BodyTooLarge(f"body exceeds {MAX_JSON_BODY} bytes")
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _check_host(handler: BaseHTTPRequestHandler) -> bool:
    bind = os.environ.get("ATELIER_HOST", "127.0.0.1").strip() or "127.0.0.1"
    if bind not in LOCAL_BINDS:
        return True
    host = (handler.headers.get("Host") or "").split(":")[0].lower()
    if host in {"127.0.0.1", "localhost", "localhost.", "::1", ""}:
        return True
    _json(handler, 403, {"error": "refusing non-local Host", "code": "bad_host"})
    return False


def _send_web(handler: BaseHTTPRequestHandler, rel: str) -> None:
    safe = safe_under(WEB, WEB / rel)
    if not safe:
        _json(handler, 404, {"error": "not found"})
        return
    _send_file(handler, safe)


def _send_file(
    handler: BaseHTTPRequestHandler,
    path: Path,
    download_name: str | None = None,
    mime: str | None = None,
) -> None:
    if not path.exists() or not path.is_file():
        _json(handler, 404, {"error": "not found"})
        return
    data = path.read_bytes()
    guessed = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
    if path.suffix == ".svg":
        guessed = "image/svg+xml"
    mime = (mime or guessed).split(";")[0].strip() or guessed
    handler.send_response(200)
    handler.send_header("Content-Type", mime)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("X-Content-Type-Options", "nosniff")
    if mime.startswith("image/svg"):
        handler.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; sandbox",
        )
    if download_name:
        handler.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
    handler.end_headers()
    handler.wfile.write(data)


def _send_bytes(handler: BaseHTTPRequestHandler, data: bytes, mime: str, download_name: str) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", mime)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Content-Disposition", f'attachment; filename="{download_name}"')
    handler.send_header("X-Content-Type-Options", "nosniff")
    if (mime or "").startswith("image/svg"):
        handler.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; sandbox",
        )
    handler.end_headers()
    handler.wfile.write(data)


def _sse_result(handler: BaseHTTPRequestHandler, result: dict) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    for ev in result.get("events") or []:
        handler.wfile.write(f"event: {ev.get('kind', 'message')}\n".encode())
        handler.wfile.write(f"data: {json.dumps(ev, ensure_ascii=False, default=str)}\n\n".encode())
    handler.wfile.write(b"event: result\n")
    handler.wfile.write(f"data: {json.dumps(result, ensure_ascii=False, default=str)}\n\n".encode())
    handler.wfile.flush()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("atelier %s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self) -> None:
        if not _check_host(self):
            return
        with get_app().lock:
            self._do_GET()

    def _do_GET(self) -> None:
        app = get_app()
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        if path in {"/", "/index.html"}:
            _send_web(self, "index.html")
            return
        if path.startswith("/web/"):
            _send_web(self, path[len("/web/") :])
            return
        if path.startswith("/assets/"):
            _send_web(self, path[len("/assets/") :])
            return
        if path in {"/app.js", "/styles.css"}:
            _send_web(self, path.lstrip("/"))
            return
        if path == "/api/health":
            _json(
                self,
                200,
                {
                    "ok": True,
                    "name": "atelier",
                    "architecture": "helix",
                    "evolve_rounds": 20,
                },
            )
            return
        if path == "/api/keys":
            _json(self, 200, app.keyring.public_status())
            return
        if path == "/api/projects":
            _json(self, 200, {"projects": app.memory.list_projects()})
            return
        if path == "/api/catalog":
            _json(self, 200, catalog_public())
            return
        if path == "/api/usage":
            _json(self, 200, {"events": app.memory.list_usage(), "totals": app.memory.usage_totals()})
            return
        parts = [p for p in path.split("/") if p]
        if parts[:2] == ["api", "projects"] and len(parts) == 3:
            project = app.memory.get_project(parts[2])
            _json(self, 200 if project else 404, project or {"error": "missing project"})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "threads":
            _json(self, 200, {"threads": app.memory.list_threads(parts[2])})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "board":
            project = app.memory.get_project(parts[2])
            if not project:
                _json(self, 404, {"error": "missing project"})
                return
            nodes = app.memory.list_nodes(parts[2])
            _json(self, 200, {"nodes": nodes, "camera": project.get("camera") or {"x": 0, "y": 0, "zoom": 1}})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "camera":
            project = app.memory.get_project(parts[2])
            if not project:
                _json(self, 404, {"error": "missing project"})
                return
            _json(self, 200, {"camera": project.get("camera")})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "export":
            fmt = (query.get("fmt") or query.get("format") or ["zip"])[0].strip().lower()
            scale = export_scale((query.get("scale") or ["1"])[0])
            try:
                data, mime, name = export_project_bytes(
                    app.memory, app.artifacts, parts[2], fmt=fmt, scale=scale
                )
            except FormatError as exc:
                _json(self, 415, {"error": str(exc), "code": exc.code})
                return
            except ValueError as exc:
                _json(self, 404, {"error": str(exc)})
                return
            _send_bytes(self, data, mime, name)
            return
        if parts[:2] == ["api", "threads"] and len(parts) == 4 and parts[3] == "messages":
            _json(self, 200, {"messages": app.memory.list_messages(parts[2])})
            return
        if parts[:2] == ["api", "artifacts"] and len(parts) == 4 and parts[3] == "export":
            art = app.memory.get_artifact(parts[2])
            if not art:
                _json(self, 404, {"error": "missing artifact"})
                return
            fmt = (query.get("fmt") or query.get("format") or ["native"])[0].strip().lower()
            scale = export_scale((query.get("scale") or ["1"])[0])
            try:
                data, mime, name = export_artifact_bytes(art, app.artifacts, fmt=fmt, scale=scale)
            except FormatError as exc:
                _json(self, 415, {"error": str(exc), "code": exc.code})
                return
            except FileNotFoundError:
                _json(self, 404, {"error": "not found"})
                return
            _send_bytes(self, data, mime, name)
            return
        if parts[:2] == ["api", "artifacts"] and len(parts) == 3:
            art = app.memory.get_artifact(parts[2])
            if not art:
                _json(self, 404, {"error": "missing artifact"})
                return
            name = download_filename(art)
            force = query.get("download", ["0"])[0].strip().lower() in {"1", "true", "yes", "on"}
            safe = safe_under(app.artifacts, Path(art["path"]))
            if not safe:
                _json(self, 404, {"error": "not found"})
                return
            _send_file(self, safe, download_name=name if force else None, mime=art.get("mime"))
            return
        if path.startswith("/api/"):
            _json(self, 404, {"error": "unknown GET"})
            return
        _send_web(self, path.lstrip("/"))

    def do_POST(self) -> None:
        if not _check_host(self):
            return
        with get_app().lock:
            self._do_POST()

    def _do_POST(self) -> None:
        app = get_app()
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        try:
            body = _read_json(self)
        except BodyTooLarge as exc:
            _json(self, 413, {"error": str(exc)})
            return
        except json.JSONDecodeError:
            _json(self, 400, {"error": "invalid json"})
            return
        parts = [p for p in path.split("/") if p]

        if path == "/api/keys":
            try:
                _json(
                    self,
                    200,
                    app.keyring.put(
                        body.get("provider", ""),
                        key=body.get("key") or "",
                        base_url=body.get("base_url") or "",
                    ),
                )
            except ValueError as exc:
                _json(self, 400, {"error": str(exc), "code": "unofficial_host"})
            return
        if path == "/api/quote":
            _json(
                self,
                200,
                quote_run(
                    provider=body.get("provider") or "demo",
                    model=body.get("model") or "",
                    prompt=body.get("prompt") or "",
                    count=as_int(body.get("count") or body.get("variants") or 1, default=1, lo=1, hi=4),
                    capability=body.get("capability") or "image",
                    memory=app.memory,
                    thread_id=body.get("thread_id"),
                ),
            )
            return
        if path == "/api/projects":
            project = app.memory.create_project(body.get("name") or "Untitled")
            app.memory.create_thread(project["id"], topic="New thread", mode=body.get("mode") or "fast")
            _json(self, 201, project)
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "threads":
            if not app.memory.get_project(parts[2]):
                _json(self, 404, {"error": "missing project"})
                return
            thread = app.memory.create_thread(
                parts[2],
                topic=body.get("topic") or "",
                mode=body.get("mode") or "fast",
            )
            _json(self, 201, thread)
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "brand":
            project = app.memory.update_brand_kit(parts[2], body.get("brand_kit") or body)
            _json(self, 200 if project else 404, project or {"error": "missing project"})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "camera":
            project = app.memory.set_camera(parts[2], body.get("camera") or body)
            _json(self, 200 if project else 404, project or {"error": "missing project"})
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "undo":
            _json(self, 200, app.memory.undo(parts[2]))
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "nodes":
            if not app.memory.get_project(parts[2]):
                # Nodes carry no foreign key, so a typo'd id used to mint a card
                # onto a board that can never be opened again.
                _json(self, 404, {"error": "missing project"})
                return
            node = app.memory.add_node(
                project_id=parts[2],
                type=body.get("type") or "text",
                text=body.get("text") or body.get("data") or "",
                x=body.get("x", 80),
                y=body.get("y", 80),
                w=body.get("w", 280),
                h=body.get("h", 120),
                meta=body.get("meta") or {"layer": "text"},
            )
            _json(self, 201, node)
            return
        if parts[:2] == ["api", "projects"] and len(parts) == 4 and parts[3] == "upload":
            project = app.memory.get_project(parts[2])
            if not project:
                _json(self, 404, {"error": "missing project"})
                return
            raw_b64 = body.get("data") or body.get("content") or ""
            if not isinstance(raw_b64, str) or not raw_b64.strip():
                _json(self, 400, {"error": "empty upload"})
                return
            if len(raw_b64) > 6_800_000:  # > 5 MB once decoded; skip the decode
                _json(self, 413, {"error": "upload too large"})
                return
            raw_b64 = "".join(raw_b64.split())  # tolerate wrapped base64
            try:
                blob = base64.b64decode(raw_b64, validate=True)
            except Exception:
                _json(self, 400, {"error": "invalid base64"})
                return
            if not blob:
                _json(self, 400, {"error": "empty upload"})
                return
            if len(blob) > 5_000_000:
                _json(self, 413, {"error": "upload too large"})
                return
            mime = (body.get("mime") or "application/octet-stream").split(";")[0].strip().lower()
            if not (mime.startswith("image/") or mime in UPLOAD_MIME_OK):
                mime = "application/octet-stream"
            filename = body.get("filename") or "upload.bin"
            art = app.memory.add_artifact(
                project_id=parts[2],
                kind="upload",
                mime=mime,
                prompt=filename,
                provider="local",
                model="upload",
            )
            path = write_bytes(app.artifacts, art["id"], blob, mime)
            app.memory.conn.execute("UPDATE artifacts SET path=? WHERE id=?", (str(path), art["id"]))
            app.memory.conn.commit()
            art["path"] = str(path)
            existing = len(app.memory.list_nodes(parts[2]))
            node = app.memory.add_node(
                project_id=parts[2],
                type="image" if mime.startswith("image/") else "note",
                artifact_id=art["id"],
                text=filename,
                x=72 + (existing % 3) * 360,
                y=72 + (existing // 3) * 280,
            )
            _json(self, 201, {"artifact": art, "node": node})
            return
        if parts[:2] == ["api", "threads"] and len(parts) == 4 and parts[3] == "run":
            thread = app.memory.get_thread(parts[2])
            if not thread:
                _json(self, 404, {"error": "missing thread"})
                return
            stream = query.get("stream", ["0"])[0] in {"1", "true", "yes"}
            try:
                result = app.conductor.run(
                    project_id=thread["project_id"],
                    thread_id=thread["id"],
                    prompt=body.get("prompt") or "",
                    mode=body.get("mode") or thread.get("mode") or "fast",
                    provider=body.get("provider") or "demo",
                    model=body.get("model") or "",
                    variants=as_int(body.get("variants") or 0, default=0, lo=0, hi=4),
                    parent_artifact_id=body.get("parent_artifact_id") or body.get("spot_artifact_id"),
                )
            except BudgetExceeded as exc:
                _json(self, 402, {"error": str(exc), "code": "budget_exceeded", "ok": False})
                return
            except ConductorError as exc:
                _json(self, 422, {"error": str(exc), "code": exc.code, "ok": False})
                return
            except Exception as exc:
                _json(self, 500, {"error": str(exc), "ok": False})
                return
            if stream:
                _sse_result(self, result)
                return
            _json(self, 200, result)
            return
        if parts[:2] == ["api", "nodes"] and len(parts) == 3:
            node = app.memory.update_node(parts[2], **{k: body[k] for k in body})
            _json(self, 200 if node else 404, node or {"error": "missing node"})
            return
        _json(self, 404, {"error": "unknown POST"})

    def do_DELETE(self) -> None:
        if not _check_host(self):
            return
        with get_app().lock:
            self._do_DELETE()

    def _do_DELETE(self) -> None:
        app = get_app()
        parts = [p for p in urlparse(self.path).path.split("/") if p]
        if parts[:2] == ["api", "nodes"] and len(parts) == 3:
            ok = app.memory.delete_node(parts[2])
            _json(self, 200 if ok else 404, {"ok": ok})
            return
        _json(self, 404, {"error": "unknown DELETE"})

    def do_PATCH(self) -> None:
        self.do_POST()


def main(host: str | None = None, port: int | None = None) -> None:
    from atelier.launch import DEFAULT_HOST, DEFAULT_PORT, env_host, env_port

    host = (host or "").strip() or env_host() or DEFAULT_HOST
    port = int(port) if port is not None else (env_port() or DEFAULT_PORT)
    # _check_host reads ATELIER_HOST; keep it honest about what --host bound,
    # or `--host 0.0.0.0` binds the LAN and then 403s every LAN client.
    os.environ["ATELIER_HOST"] = host
    try:
        server = ThreadingHTTPServer((host, port), Handler)
    except (OSError, OverflowError) as exc:
        detail = getattr(exc, "strerror", None) or exc
        print(f"atelier: cannot bind {host}:{port} — {detail}", file=sys.stderr, flush=True)
        raise SystemExit(1) from None
    bound = server.server_address
    host, port = bound[0], bound[1]
    shown = f"[{host}]" if ":" in str(host) else host
    print(f"Atelier Helix on http://{shown}:{port}", flush=True)
    print("BYOK: OPENAI_API_KEY / GEMINI_API_KEY or Settings panel", flush=True)
    if host not in LOCAL_BINDS:
        print(
            f"atelier: {host} is reachable off this machine — the Host guard is off",
            file=sys.stderr,
            flush=True,
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstop", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
