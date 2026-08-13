from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .config import ForcedModelConfig, dump_public
from .rewrite import extract_model, rewrite_cursor_agent, rewrite_payload


def _json_bytes(payload: dict[str, Any], status: int = 200) -> tuple[int, bytes, str]:
    return status, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json"


def handle_request(
    method: str,
    path: str,
    body: dict[str, Any] | None,
    cfg: ForcedModelConfig,
    *,
    upstream: str | None = None,
) -> tuple[int, bytes, str]:
    parsed = urlparse(path)
    route = parsed.path.rstrip("/") or "/"

    if method == "GET" and route in {"/health", "/"}:
        return _json_bytes({"ok": True, "forced_model": cfg.spec.cli_model})
    if method == "GET" and route == "/config":
        return _json_bytes(dump_public(cfg))
    if method == "GET" and route == "/v1/models":
        models = [
            {"id": cfg.spec.cli_model, "forced": True},
            {"id": cfg.spec.id, "forced": True},
            *[{"id": alias, "maps_to": cfg.spec.cli_model} for alias in sorted(cfg.auto_aliases)],
        ]
        return _json_bytes({"object": "list", "data": models})

    payload = body or {}
    original = extract_model(payload)

    if method == "POST" and route in {"/v1/rewrite", "/rewrite"}:
        rewritten = rewrite_payload(payload, cfg, for_api=False)
        return _json_bytes(
            {
                "original_model": original,
                "model": rewritten.get("model"),
                "body": rewritten,
            }
        )

    if method == "POST" and route == "/v1/agents":
        rewritten = rewrite_cursor_agent(payload, cfg)
        if upstream:
            return _proxy(upstream, "/v1/agents", rewritten)
        return _json_bytes(
            {
                "rewritten": True,
                "original_model": original,
                "model": rewritten.get("model"),
                "body": rewritten,
            }
        )

    if method == "POST" and route in {"/v1/chat/completions", "/v1/messages"}:
        for_api = route == "/v1/messages"
        rewritten = rewrite_payload(payload, cfg, for_api=for_api)
        if upstream:
            return _proxy(upstream, route, rewritten)
        return _json_bytes(
            {
                "rewritten": True,
                "object": "chat.completion" if route.endswith("completions") else "message",
                "original_model": original,
                "model": rewritten.get("model"),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                f"Forced Auto/model {original!r} → {rewritten.get('model')}. "
                                "Set UPSTREAM_BASE_URL to proxy to a real provider."
                            ),
                        },
                    }
                ],
            }
        )

    return _json_bytes({"error": f"unsupported {method} {route}"}, HTTPStatus.NOT_FOUND)


def _proxy(upstream: str, route: str, payload: dict[str, Any]) -> tuple[int, bytes, str]:
    url = upstream.rstrip("/") + route
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(req, timeout=60) as resp:  # noqa: S310 - user-configured upstream
        return resp.status, resp.read(), resp.headers.get("Content-Type", "application/json")


def make_handler(cfg: ForcedModelConfig, upstream: str | None):
    class Handler(BaseHTTPRequestHandler):
        def _read_json(self) -> dict[str, Any] | None:
            length = int(self.headers.get("Content-Length") or 0)
            if not length:
                return None
            raw = self.rfile.read(length)
            if not raw:
                return None
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("JSON body must be an object")
            return data

        def _write(self, status: int, data: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:  # noqa: N802
            status, data, ctype = handle_request("GET", self.path, None, cfg, upstream=upstream)
            self._write(status, data, ctype)

        def do_POST(self) -> None:  # noqa: N802
            try:
                body = self._read_json()
            except Exception as exc:
                self._write(
                    HTTPStatus.BAD_REQUEST,
                    json.dumps({"error": str(exc)}).encode("utf-8"),
                    "application/json",
                )
                return
            status, data, ctype = handle_request("POST", self.path, body, cfg, upstream=upstream)
            self._write(status, data, ctype)

        def log_message(self, fmt: str, *args: Any) -> None:
            sys_stderr = __import__("sys").stderr
            sys_stderr.write("forced-router: " + (fmt % args) + "\n")

    return Handler


def serve(cfg: ForcedModelConfig, host: str = "127.0.0.1", port: int = 8788, upstream: str | None = None):
    httpd = ThreadingHTTPServer((host, port), make_handler(cfg, upstream))
    print(f"forced-router listening on http://{host}:{httpd.server_port} → {cfg.spec.cli_model}", flush=True)
    httpd.serve_forever()
    return httpd
