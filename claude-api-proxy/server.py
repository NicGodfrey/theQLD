"""Anthropic Messages API compatible reverse proxy (stdlib only).

POST /v1/messages   - official request/response shape, SSE streaming supported
GET  /v1/models     - model catalog
GET  /health        - liveness

Callers authenticate with x-api-key == CLAUDE_PROXY_API_KEY. Requests are
forwarded to an upstream Anthropic-compatible API (ANTHROPIC_API_KEY /
ANTHROPIC_BASE_URL) with the preset system prompt from prompts/system.md
prepended to any caller-supplied `system`.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ANTHROPIC_VERSION = "2023-06-01"
UPSTREAM_TIMEOUT_S = 600

FORWARDED_FIELDS = frozenset(
    {
        "model",
        "max_tokens",
        "messages",
        "system",
        "stream",
        "temperature",
        "top_p",
        "top_k",
        "stop_sequences",
        "metadata",
        "tools",
        "tool_choice",
        "thinking",
    }
)

MODELS = [
    {"type": "model", "id": "claude-fable-5", "display_name": "Claude Fable 5", "created_at": "2026-07-15T00:00:00Z"},
    {"type": "model", "id": "claude-sonnet-5", "display_name": "Claude Sonnet 5", "created_at": "2026-07-15T00:00:00Z"},
    {"type": "model", "id": "claude-opus-4-8", "display_name": "Claude Opus 4.8", "created_at": "2026-03-01T00:00:00Z"},
    {"type": "model", "id": "claude-haiku-4-5-20251001", "display_name": "Claude Haiku 4.5", "created_at": "2025-10-01T00:00:00Z"},
]

_system_prompt_cache = None


def get_system_prompt():
    global _system_prompt_cache
    if _system_prompt_cache is None:
        path = os.path.join(BASE_DIR, "prompts", "system.md")
        with open(path, "r", encoding="utf-8") as f:
            _system_prompt_cache = f.read().strip()
    return _system_prompt_cache


def error_body(err_type, message):
    return {"type": "error", "error": {"type": err_type, "message": message}}


def validate_messages_request(body):
    """Return an error message string, or None when the request is valid."""
    if not isinstance(body, dict):
        return "body: input must be a JSON object"
    model = body.get("model")
    if not isinstance(model, str) or not model:
        return "model: field required"
    max_tokens = body.get("max_tokens")
    if not isinstance(max_tokens, int) or isinstance(max_tokens, bool) or max_tokens < 1:
        return "max_tokens: field required and must be a positive integer"
    messages = body.get("messages")
    if not isinstance(messages, list) or not messages:
        return "messages: field required and must be a non-empty array"
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return "messages.%d: must be an object with role and content" % i
        if msg.get("role") not in ("user", "assistant"):
            return "messages.%d.role: must be one of 'user' or 'assistant'" % i
        if "content" not in msg:
            return "messages.%d.content: field required" % i
    system = body.get("system")
    if system is not None and not isinstance(system, (str, list)):
        return "system: must be a string or an array of content blocks"
    return None


def inject_system(body, proxy_system):
    """Prepend the proxy system prompt to any caller-supplied system."""
    blocks = [{"type": "text", "text": proxy_system}]
    caller = body.get("system")
    if isinstance(caller, str):
        if caller:
            blocks.append({"type": "text", "text": caller})
    elif isinstance(caller, list):
        blocks.extend(caller)
    out = dict(body)
    out["system"] = blocks
    return out


def build_upstream_body(body, proxy_system):
    filtered = {k: v for k, v in body.items() if k in FORWARDED_FIELDS}
    return inject_system(filtered, proxy_system)


def upstream_config():
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_UPSTREAM_API_KEY")
    base = (
        os.environ.get("ANTHROPIC_BASE_URL")
        or os.environ.get("CLAUDE_UPSTREAM_BASE_URL")
        or "https://api.anthropic.com"
    ).rstrip("/")
    return key, base


def proxy_api_key():
    return os.environ.get("CLAUDE_PROXY_API_KEY", "sk-proxy-local")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "claude-api-proxy/1.0"

    def log_message(self, fmt, *args):
        # Default request-line logging only; never log headers or keys.
        BaseHTTPRequestHandler.log_message(self, fmt, *args)

    def _send_json(self, status, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_raw(self, status, content_type, payload):
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _authorized(self):
        return self.headers.get("x-api-key") == proxy_api_key()

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"ok": True, "api_style": "anthropic-messages-v1"})
            return
        if not self._authorized():
            self._send_json(401, error_body("authentication_error", "invalid x-api-key"))
            return
        if self.path == "/v1/models":
            self._send_json(
                200,
                {
                    "data": MODELS,
                    "first_id": MODELS[0]["id"],
                    "last_id": MODELS[-1]["id"],
                    "has_more": False,
                },
            )
            return
        self._send_json(404, error_body("not_found_error", "Not found: %s" % self.path))

    def do_POST(self):
        if not self._authorized():
            self._send_json(401, error_body("authentication_error", "invalid x-api-key"))
            return
        if self.path != "/v1/messages":
            self._send_json(404, error_body("not_found_error", "Not found: %s" % self.path))
            return

        try:
            length = int(self.headers.get("content-length") or 0)
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, error_body("invalid_request_error", "body: invalid JSON"))
            return

        err = validate_messages_request(body)
        if err:
            self._send_json(400, error_body("invalid_request_error", err))
            return

        key, base = upstream_config()
        if not key:
            self._send_json(
                503,
                error_body(
                    "api_error",
                    "This proxy has no upstream Anthropic API key configured. "
                    "Set ANTHROPIC_API_KEY (or CLAUDE_UPSTREAM_API_KEY) on the server.",
                ),
            )
            return

        upstream_body = build_upstream_body(body, get_system_prompt())
        streaming = bool(body.get("stream"))
        req = urlrequest.Request(
            base + "/v1/messages",
            data=json.dumps(upstream_body).encode("utf-8"),
            method="POST",
            headers={
                "x-api-key": key,
                "anthropic-version": self.headers.get("anthropic-version", DEFAULT_ANTHROPIC_VERSION),
                "content-type": "application/json",
                "accept": "text/event-stream" if streaming else "application/json",
            },
        )

        try:
            resp = urlrequest.urlopen(req, timeout=UPSTREAM_TIMEOUT_S)
        except HTTPError as e:
            payload = e.read()
            self._send_raw(e.code, e.headers.get("content-type", "application/json"), payload)
            return
        except URLError as e:
            self._send_json(502, error_body("api_error", "upstream unreachable: %s" % e.reason))
            return

        with resp:
            if streaming:
                self._pipe_sse(resp)
            else:
                payload = resp.read()
                self._send_raw(resp.status, resp.headers.get("content-type", "application/json"), payload)

    def _pipe_sse(self, resp):
        self.send_response(resp.status)
        self.send_header("content-type", resp.headers.get("content-type", "text/event-stream"))
        self.send_header("cache-control", "no-cache")
        self.send_header("connection", "close")
        self.close_connection = True
        self.end_headers()
        try:
            while True:
                chunk = resp.read1(65536)
                if not chunk:
                    break
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    get_system_prompt()
    key, base = upstream_config()
    upstream = "upstream: " + base if key else "upstream: NOT CONFIGURED (requests will get 503)"
    print("claude-api-proxy listening on %s:%d (%s)" % (host, port, upstream))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
