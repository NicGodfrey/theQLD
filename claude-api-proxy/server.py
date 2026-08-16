"""Claude Messages API facade over this Cursor Cloud Agent (stdlib only).

Remote callers use the official Anthropic Messages shape. This process turns
each request into a follow-up run on CURSOR_AGENT_ID via api.cursor.com.
"""

import json
import os
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

import cursor_backend

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
_cursor_lock = threading.Lock()


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


def anthropic_config():
    key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_UPSTREAM_API_KEY")
    base = (
        os.environ.get("ANTHROPIC_BASE_URL")
        or os.environ.get("CLAUDE_UPSTREAM_BASE_URL")
        or "https://api.anthropic.com"
    ).rstrip("/")
    return key, base


def proxy_api_key():
    return os.environ.get("CLAUDE_PROXY_API_KEY", "sk-proxy-local")


def active_backend():
    cursor_key, agent_id, cursor_base = cursor_backend.cursor_config()
    if cursor_key:
        return "cursor", cursor_key, agent_id, cursor_base
    anth_key, anth_base = anthropic_config()
    if anth_key:
        return "anthropic", anth_key, None, anth_base
    return None, None, None, None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "claude-api-proxy/1.1"

    def log_message(self, fmt, *args):
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
            backend, _, agent_id, _ = active_backend()
            self._send_json(
                200,
                {
                    "ok": True,
                    "api_style": "anthropic-messages-v1",
                    "backend": backend or "unconfigured",
                    "agent_id": agent_id,
                },
            )
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

        backend, key, agent_id, base = active_backend()
        if backend is None:
            self._send_json(
                503,
                error_body(
                    "api_error",
                    "Set CURSOR_API_KEY to export this Cursor Cloud Agent over the Claude Messages API. "
                    "Optional fallback: ANTHROPIC_API_KEY for a plain Anthropic reverse proxy.",
                ),
            )
            return

        if backend == "cursor":
            self._handle_cursor(body, key, agent_id, base)
            return
        self._handle_anthropic(body, key, base)

    def _handle_cursor(self, body, api_key, agent_id, base):
        prompt_text = cursor_backend.build_followup_text(body, get_system_prompt())
        model = body.get("model") or "claude-fable-5"
        streaming = bool(body.get("stream"))
        try:
            with _cursor_lock:
                run_id = cursor_backend.create_run(api_key, agent_id, base, prompt_text)
                if streaming:
                    self._stream_cursor_run(api_key, agent_id, base, run_id, model)
                    return
                run = cursor_backend.wait_for_run(api_key, agent_id, base, run_id, UPSTREAM_TIMEOUT_S)
        except HTTPError as e:
            payload = e.read()
            try:
                parsed = json.loads(payload.decode("utf-8"))
                message = parsed.get("message") or parsed.get("error") or payload.decode("utf-8", "replace")
            except (ValueError, UnicodeDecodeError):
                message = "cursor API error %s" % e.code
            self._send_json(e.code if e.code >= 400 else 502, error_body("api_error", str(message)))
            return
        except URLError as e:
            self._send_json(502, error_body("api_error", "cursor API unreachable: %s" % e.reason))
            return
        except TimeoutError as e:
            self._send_json(504, error_body("api_error", str(e)))
            return
        except RuntimeError as e:
            self._send_json(502, error_body("api_error", str(e)))
            return

        status = (run.get("status") or "").upper()
        text = run.get("result") or ""
        if status != "FINISHED":
            self._send_json(
                502,
                error_body("api_error", "cursor run %s ended with status %s" % (run.get("id"), status)),
            )
            return
        self._send_json(200, cursor_backend.claude_message(text, model))

    def _stream_cursor_run(self, api_key, agent_id, base, run_id, model):
        message_id = "msg_%s" % uuid.uuid4().hex
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.send_header("connection", "close")
        self.close_connection = True
        self.end_headers()
        try:
            self.wfile.write(cursor_backend.anthropic_stream_open(model, message_id).encode("utf-8"))
            self.wfile.flush()
            url = "%s/v1/agents/%s/runs/%s/stream" % (base, agent_id, run_id)
            req = urlrequest.Request(
                url,
                method="GET",
                headers={
                    "authorization": cursor_backend.basic_auth_header(api_key),
                    "accept": "text/event-stream",
                },
            )
            with urlrequest.urlopen(req, timeout=UPSTREAM_TIMEOUT_S) as resp:
                buf = ""
                while True:
                    chunk = resp.read1(65536)
                    if not chunk:
                        break
                    buf += chunk.decode("utf-8", "replace")
                    while "\n\n" in buf:
                        raw_event, buf = buf.split("\n\n", 1)
                        for name, payload in cursor_backend.parse_sse_events(raw_event + "\n\n"):
                            if name == "assistant" and isinstance(payload, dict) and payload.get("text"):
                                self.wfile.write(cursor_backend.anthropic_stream_delta(payload["text"]).encode("utf-8"))
                                self.wfile.flush()
                            elif name == "result" and isinstance(payload, dict) and payload.get("text"):
                                # Final text is also emitted as assistant deltas; ignore duplicate if empty.
                                if payload["text"] and not payload.get("status"):
                                    pass
            self.wfile.write(cursor_backend.anthropic_stream_close().encode("utf-8"))
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except (HTTPError, URLError, TimeoutError):
            try:
                self.wfile.write(cursor_backend.anthropic_stream_close().encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass

    def _handle_anthropic(self, body, key, base):
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
            else:
                payload = resp.read()
                self._send_raw(resp.status, resp.headers.get("content-type", "application/json"), payload)


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8080"))
    get_system_prompt()
    backend, _, agent_id, base = active_backend()
    if backend == "cursor":
        upstream = "backend=cursor agent=%s api=%s" % (agent_id, base)
    elif backend == "anthropic":
        upstream = "backend=anthropic %s" % base
    else:
        upstream = "backend=unconfigured (set CURSOR_API_KEY)"
    print("claude-api-proxy listening on %s:%d (%s)" % (host, port, upstream))
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
