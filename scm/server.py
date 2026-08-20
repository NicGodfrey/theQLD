#!/usr/bin/env python3
"""Stdlib HTTP sidecar that mounts the SCM onto this Cloud Agent / local machine."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from store import ScmStore  # noqa: E402

HOST = os.environ.get("SCM_HOST", "127.0.0.1")
PORT = int(os.environ.get("SCM_PORT", "8787"))
COLLECTION_ROUTES = {
    "suppliers": "suppliers",
    "products": "products",
    "warehouses": "warehouses",
    "purchase-orders": "purchaseOrders",
    "sales-orders": "salesOrders",
    "shipments": "shipments",
    "movements": "movements",
}


def json_bytes(payload: object, status: int = 200) -> tuple[int, bytes, str]:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return status, body, "application/json; charset=utf-8"


class ScmHandler(BaseHTTPRequestHandler):
    store: ScmStore

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send(204, b"", "text/plain")

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        try:
            self._dispatch_get()
        except Exception as exc:  # pragma: no cover - defensive
            self._send(*json_bytes({"error": str(exc), "trace": traceback.format_exc()}, 500))

    def do_POST(self) -> None:  # noqa: N802
        self._mutate("POST")

    def do_PUT(self) -> None:  # noqa: N802
        self._mutate("PUT")

    def do_DELETE(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) == 3 and parts[0] == "api" and parts[1] in COLLECTION_ROUTES:
                kind = COLLECTION_ROUTES[parts[1]]
                deleted = self.store.delete(kind, parts[2])
                self._send(*json_bytes({"deleted": deleted}, 200 if deleted else 404))
                return
            self._send(*json_bytes({"error": "not found"}, 404))
        except ValueError as exc:
            self._send(*json_bytes({"error": str(exc)}, 400))
        except Exception as exc:  # pragma: no cover
            self._send(*json_bytes({"error": str(exc), "trace": traceback.format_exc()}, 500))

    def _read_json(self) -> object:
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        if not raw.strip():
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc

    def _dispatch_get(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            self._api_get(path, parse_qs(parsed.query))
            return
        self._static(path)

    def _api_get(self, path: str, query: dict[str, list[str]]) -> None:
        parts = [p for p in path.split("/") if p]
        if parts == ["api", "health"]:
            self._send(*json_bytes({"ok": True, "service": "scm"}))
            return
        if parts == ["api", "state"] or parts == ["api", "export"]:
            self._send(*json_bytes(self.store.export()))
            return
        if parts == ["api", "dashboard"]:
            self._send(*json_bytes(self.store.dashboard()))
            return
        if len(parts) == 2 and parts[0] == "api" and parts[1] in COLLECTION_ROUTES:
            kind = COLLECTION_ROUTES[parts[1]]
            self._send(*json_bytes(self.store.export().get(kind, [])))
            return
        if len(parts) == 3 and parts[0] == "api" and parts[1] in COLLECTION_ROUTES:
            kind = COLLECTION_ROUTES[parts[1]]
            item_id = parts[2]
            for row in self.store.export().get(kind, []):
                if row.get("id") == item_id:
                    self._send(*json_bytes(row))
                    return
            self._send(*json_bytes({"error": "not found"}, 404))
            return
        self._send(*json_bytes({"error": "not found"}, 404))

    def _mutate(self, method: str) -> None:
        try:
            parsed = urlparse(self.path)
            parts = [p for p in parsed.path.split("/") if p]
            payload = self._read_json()
            if parts == ["api", "mount"] and method == "POST":
                if not isinstance(payload, dict):
                    raise ValueError("mount body must be an object")
                data = payload.get("data", payload)
                mode = str(payload.get("mode") or "replace")
                source = str(payload.get("source") or data.get("source") or "local-mount")
                if mode == "merge":
                    state = self.store.merge(data, source=source)
                else:
                    state = self.store.replace(data, source=source)
                self._send(*json_bytes({"ok": True, "mode": mode, "state": state}))
                return
            if parts == ["api", "state"] and method == "PUT":
                state = self.store.replace(payload)
                self._send(*json_bytes(state))
                return
            if parts == ["api", "stock", "adjust"] and method == "POST":
                if not isinstance(payload, dict):
                    raise ValueError("adjust body must be an object")
                movement = self.store.adjust_stock(
                    str(payload.get("warehouseId") or ""),
                    str(payload.get("productId") or ""),
                    float(payload.get("qty") or 0),
                    str(payload.get("type") or "adjust"),
                    str(payload.get("ref") or ""),
                )
                self._send(*json_bytes(movement))
                return
            if len(parts) >= 2 and parts[0] == "api" and parts[1] in COLLECTION_ROUTES:
                kind = COLLECTION_ROUTES[parts[1]]
                if not isinstance(payload, dict):
                    raise ValueError("body must be an object")
                if len(parts) == 3:
                    payload = dict(payload)
                    payload["id"] = parts[2]
                item = self.store.upsert(kind, payload)
                self._send(*json_bytes(item, 201 if method == "POST" else 200))
                return
            self._send(*json_bytes({"error": "not found"}, 404))
        except ValueError as exc:
            self._send(*json_bytes({"error": str(exc)}, 400))
        except Exception as exc:  # pragma: no cover
            self._send(*json_bytes({"error": str(exc), "trace": traceback.format_exc()}, 500))

    def _static(self, path: str) -> None:
        relative = path.lstrip("/") or "index.html"
        if relative.endswith("/"):
            relative += "index.html"
        target = (ROOT / relative).resolve()
        if not str(target).startswith(str(ROOT)) or not target.is_file():
            index = ROOT / "index.html"
            if index.is_file() and "." not in Path(relative).name:
                target = index
            else:
                self._send(*json_bytes({"error": "not found"}, 404))
                return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or target.suffix in {".js", ".json", ".svg"}:
            content_type += "; charset=utf-8"
        self._send(200, target.read_bytes(), content_type)


def make_server(host: str, port: int, db_path: Path | None = None) -> ThreadingHTTPServer:
    handler = ScmHandler
    handler.store = ScmStore(db_path)
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mount and serve the supply-chain sidecar")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--db", default=os.environ.get("SCM_DB", str(ROOT / "data" / "scm.sqlite")))
    args = parser.parse_args()
    httpd = make_server(args.host, args.port, Path(args.db))
    print(f"SCM mounted at http://{args.host}:{args.port}/", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        ScmHandler.store.close()


if __name__ == "__main__":
    main()
